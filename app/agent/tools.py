from sqlalchemy.orm import Session

from app.services.product_repo import ProductRepository
from app.rag.vector_store import ProductVectorStore
from app.agent.normalizers import normalize_skin_type, normalize_category


vector_store = ProductVectorStore()


def _format_product(product) -> dict:
    return {
        "id": product.id,
        "name": product.name,
        "brand": product.brand.name if product.brand else None,
        "category": product.category.name if product.category else None,
        "price": product.price,
        "currency": product.currency,
        "in_stock": product.in_stock,
        "skin_type": product.skin_type,
        "spf": product.spf,
        "ingredients": product.ingredients,
        "description": product.description,
        "volume_ml": product.volume_ml,
        "key_features": product.key_features,
        "verification_status": product.verification_status,
    }


def search_products(
    db: Session,
    keyword: str | None = None,
    skin_type: str | None = None,
    category: str | None = None,
    brand: str | None = None,
    min_spf: int | None = None,
    limit: int = 5,
) -> list[dict]:

    products = ProductRepository.search_products(
        db=db,
        keyword=keyword,
        skin_type=skin_type,
        category_name=category,
        brand_name=brand,
        min_spf=min_spf,
        limit=min(max(limit, 1), 10),
    )

    return [_format_product(product) for product in products]


def semantic_search_products(
    query: str,
    n_results: int = 3,
) -> list[dict]:

    results = vector_store.semantic_search(
        query=query,
        n_results=min(max(n_results, 1), 10),
    )

    formatted_results = []

    if not results or not results.get("documents"):
        return formatted_results

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        formatted_results.append({
            "product_id": metadata.get("product_id"),
            "name": metadata.get("name"),
            "brand": metadata.get("brand"),
            "category": metadata.get("category"),
            "distance": float(distance),
            "semantic_match_details": document,
        })

    return formatted_results


def hybrid_search_products(
    db: Session,
    query: str,
    skin_type: str | None = None,
    category: str | None = None,
    brand: str | None = None,
    min_spf: int | None = None,
    limit: int = 5,
) -> list[dict]:

    limit = min(max(limit, 1), 10)
    skin_type = normalize_skin_type(skin_type)
    category = normalize_category(category)

    structured_results = ProductRepository.search_products(
        db=db,
        skin_type=skin_type,
        category_name=category,
        brand_name=brand,
        min_spf=min_spf,
        limit=limit * 2,
    )

    semantic_results = semantic_search_products(
        query=query,
        n_results=limit * 2,
    )

    merged = {}

    for product in structured_results:
        merged[product.id] = {
            "product_id": product.id,
            "structured_match": True,
            "semantic_distance": None,
            "semantic_match_details": None,
        }

    # فیلترهای ساختاریافته باید روی نتایج معنایی هم اعمال شوند.
    # بنابراین محصولات خارج از دسته، نوع پوست یا SPF در نتایج نهایی نمی‌آیند.
    for result in semantic_results:
        product_id = result.get("product_id")

        if product_id is None:
            continue

        product_id = int(product_id)

        product = ProductRepository.get_product_by_id(
            db=db,
            product_id=product_id,
        )

        if product is None:
            continue

        if category and (
            not product.category
            or category.lower() not in product.category.name.lower()
        ):
            continue

        if skin_type:
            supported_types = [
                item.strip().lower()
                for item in (product.skin_type or "").split(",")
            ]

            if (
                skin_type.lower() not in supported_types
                and "all skin types" not in supported_types
            ):
                continue

        if brand and (
            not product.brand
            or brand.lower() not in product.brand.name.lower()
        ):
            continue

        if min_spf is not None and (
            product.spf is None or product.spf < min_spf
        ):
            continue

        if product_id not in merged:
            merged[product_id] = {
                "product_id": product_id,
                "structured_match": False,
                "semantic_distance": result["distance"],
                "semantic_match_details": result["semantic_match_details"],
            }
        else:
            merged[product_id]["semantic_distance"] = result["distance"]
            merged[product_id]["semantic_match_details"] = (
                result["semantic_match_details"]
            )

    ranked_ids = sorted(
        merged,
        key=lambda product_id: (
            not merged[product_id]["structured_match"],
            merged[product_id]["semantic_distance"]
            if merged[product_id]["semantic_distance"] is not None
            else float("inf"),
        ),
    )

    # وقتی کاربر فیلتر مشخصی تعیین کرده،
    # فقط محصولات دارای تطابق ساختاریافته پیشنهاد می‌شوند.
    has_hard_filters = any([
        skin_type,
        category,
        brand,
        min_spf is not None,
    ])

    if has_hard_filters:
        ranked_ids = [
            product_id
            for product_id in ranked_ids
            if merged[product_id]["structured_match"]
        ]

    final_results = []

    for product_id in ranked_ids:
        product = ProductRepository.get_product_by_id(
            db=db,
            product_id=product_id,
        )

        if product is None:
            continue

        item = _format_product(product)
        item.update(merged[product_id])

        final_results.append(item)

        if len(final_results) >= limit:
            break

    return final_results
