from app.agent.agent import format_product_response


def test_format_product_response_with_products():
    products = [
        {
            "name": "Relief Sun",
            "brand": "Beauty of Joseon",
            "category": "Sunscreen",
            "spf": 50,
            "volume_ml": 50,
            "price": 18.0,
            "currency": "USD",
            "in_stock": True,
            "description": "Lightweight sunscreen",
        }
    ]

    result = format_product_response(products, skin_type="Dry")

    assert "Relief Sun" in result
    assert "Beauty of Joseon" in result
    assert "50" in result
    assert "18.0 USD" in result
    assert "موجود" in result
    assert "پوست خشک" in result


def test_format_product_response_without_products():
    result = format_product_response([])

    assert "محصولی" in result
    assert "موجود نیست" in result


def test_format_product_response_without_skin_type():
    result = format_product_response(
        [{"name": "Hydrating Cleanser"}]
    )

    assert "Hydrating Cleanser" in result
    assert "بر اساس درخواست شما" in result


import pytest
from unittest.mock import AsyncMock, patch
from app.agent.agent import BeautyAgent


@pytest.mark.asyncio
async def test_agent_handles_greeting_without_product_search():
    agent = BeautyAgent()

    with patch(
        "app.agent.agent.ollama_client.chat",
        new_callable=AsyncMock,
    ) as mock_ollama, patch(
        "app.agent.agent.hybrid_search_products"
    ) as mock_search:

        result = await agent.chat(
            db=None,
            user_message="سلام",
        )

        assert result == "سلام! چطور می‌توانم کمکتان کنم؟"
        mock_ollama.assert_not_awaited()
        mock_search.assert_not_called()


@pytest.mark.asyncio
async def test_agent_calls_hybrid_search_with_extracted_filters():
    agent = BeautyAgent()

    agent.intent_extractor.extract = AsyncMock(
        return_value={
            "intent": "search",
            "query": "ضدآفتاب برای پوست خشک",
            "skin_type": "Dry",
            "category": "Sunscreen",
            "brand": None,
            "min_spf": 50,
        }
    )

    products = [
        {
            "name": "Relief Sun",
            "brand": "Beauty of Joseon",
            "category": "Sunscreen",
            "spf": 50,
            "price": 18.0,
            "currency": "USD",
            "in_stock": True,
        }
    ]

    with patch(
        "app.agent.agent.hybrid_search_products",
        return_value=products,
    ) as mock_search:

        result = await agent.chat(
            db=None,
            user_message="ضدآفتاب برای پوست خشک معرفی کن",
        )

        mock_search.assert_called_once_with(
            db=None,
            query="ضدآفتاب برای پوست خشک",
            skin_type="Dry",
            category="Sunscreen",
            brand=None,
            min_spf=50,
            limit=5,
        )

        assert "Relief Sun" in result
        assert "پوست خشک" in result
