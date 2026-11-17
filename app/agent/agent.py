import re
from sqlalchemy.orm import Session
from app.agent.ollama_client import ollama_client
from app.agent.tools import hybrid_search_products
from app.agent.intent_extractor import IntentExtractor

SYSTEM_PROMPT = """تو دستیار فروش یک فروشگاه آنلاین محصولات مراقبت پوستی هستی.

فقط به زبان فارسی رسمی، ساده و طبیعی پاسخ بده.
از ساختن کلمات عجیب و ترجمه کلمه‌به‌کلمه خودداری کن.
هرگز در ابتدای جمله «دستیار:» یا «پاسخ:» ننویس.

قوانین مهم:
- هرگز نوع پوست کاربر را حدس نزن.
- فقط زمانی بگو پوست کاربر چرب، خشک، مختلط یا حساس است که خودش صریحاً گفته باشد.
- اگر کاربر فقط سلام کرد، طبیعی سلام کن و بپرس چطور می‌توانی کمکش کنی.
- اگر کاربر فقط نوع پوستش را گفت، آن را تأیید کن و بپرس دنبال چه محصولی است.
- اگر کاربر درخواست محصول کرد اما نوع پوستش مشخص نبود، در صورت نیاز درباره نوع پوستش سؤال کن.
- اطلاعاتی را که کاربر نگفته به او نسبت نده.
"""

def format_product_response(products: list[dict], skin_type: str | None = None) -> str:
    if not products:
        return "متأسفانه در حال حاضر محصولی مطابق با مشخصات درخواستی شما در فروشگاه موجود نیست."

    skin_names = {
        "Oily": "چرب",
        "Dry": "خشک",
        "Combination": "مختلط",
        "Sensitive": "حساس",
        "Dehydrated": "کم‌آب",
        "All skin types": "انواع پوست",
    }

    if skin_type:
        skin_fa = skin_names.get(skin_type, skin_type)
        lines = [f"محصولات پیشنهادی برای پوست {skin_fa}:"]
    else:
        lines = ["محصولات پیشنهادی بر اساس درخواست شما:"]

    for idx, item in enumerate(products, start=1):
        lines.append("")
        lines.append(f"### {idx}. {item.get('name') or 'نامشخص'}")

        if item.get("brand"):
            lines.append(f"- **برند:** {item['brand']}")

        if item.get("category"):
            lines.append(f"- **دسته‌بندی:** {item['category']}")

        if item.get("spf") is not None:
            lines.append(f"- **SPF:** {item['spf']}")

        if item.get("volume_ml"):
            lines.append(f"- **حجم:** {item['volume_ml']}")

        if item.get("price") is not None:
            lines.append(
                f"- **قیمت:** {item['price']} {item.get('currency') or 'USD'}"
            )

        lines.append(
            f"- **وضعیت:** {'موجود' if item.get('in_stock', True) else 'ناموجود'}"
        )

        if item.get("description"):
            lines.append("")
            lines.append(f"**توضیحات:** {item['description']}")

        if item.get("key_features"):
            lines.append("")
            lines.append(f"**ویژگی‌های کلیدی:** {item['key_features']}")

        if item.get("ingredients"):
            lines.append("")
            lines.append(f"**ترکیبات:** {item['ingredients']}")

    return "\\n".join(lines).strip()


class BeautyAgent:
    def __init__(self):
        self.intent_extractor = IntentExtractor()

    async def chat(
        self,
        db: Session,
        user_message: str,
        conversation_history: list[dict] | None = None,
        history: list[dict] | None = None,
    ) -> str:
        active_history = conversation_history if conversation_history is not None else (history or [])

        # پاسخ قطعی به سلام‌های ساده
        normalized_message = user_message.strip()
        if re.fullmatch(
            r"(سلام|درود|hi|hello)[!؟?.،\s]*",
            normalized_message,
            re.IGNORECASE,
        ):
            return "سلام! چطور می‌توانم کمکتان کنم؟"

        # ۱. استخراج هدف و فیلترها
        extracted = await self.intent_extractor.extract(user_message, active_history)
        intent = extracted.get("intent", "chat")
        skin_type = extracted.get("skin_type")

        # ۲. پاسخ متنی کوتاه در حالت گفتگوی عادی
        if intent == "chat":
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                *active_history,
                {"role": "user", "content": user_message}
            ]
            response = await ollama_client.chat(messages=messages, temperature=0.1)
            raw_content = response.get("message", {}).get(
                "content",
                "سلام! متوجه شدم. دنبال چه محصول مراقبت پوستی هستید؟"
            )
            return raw_content.removeprefix("دستیار:").removeprefix("پاسخ:").strip()

        # ۳. اجرای جستجوی ترکیبی (Hybrid Search) و قالب‌بندی قطعی خروجی
        products = hybrid_search_products(
            db=db,
            query=extracted.get("query", user_message),
            skin_type=skin_type,
            category=extracted.get("category"),
            brand=extracted.get("brand"),
            min_spf=extracted.get("min_spf"),
            limit=5,
        )

        return format_product_response(products, skin_type=skin_type)


beauty_agent = BeautyAgent()
