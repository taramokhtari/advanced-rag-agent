import json
import re

from app.agent.ollama_client import ollama_client


INTENT_PROMPT = """
تو ماژول تحلیل درخواست مشتری یک فروشگاه محصولات زیبایی هستی.

پیام فعلی و تاریخچه مکالمه را بررسی کن.
فقط یک JSON معتبر برگردان و هیچ متن دیگری ننویس.

ساختار:
{
    "intent": "search" یا "chat",
    "query": "متن درخواست جستجو",
    "skin_type": null,
    "category": "Sunscreen" یا "Cleanser" یا "Serum" یا "Foundation" یا null,
    "brand": null,
    "min_spf": null
}

قوانین:
- بیان اطلاعات شخصی بدون درخواست محصول: chat
- درخواست معرفی، جستجو یا مقایسه محصول: search
- اگر دسته محصول نامشخص است، chat و درخواست توضیح بیشتر
- تاریخچه را برای درک درخواست فعلی در نظر بگیر.
- مقادیر دسته محصول باید دقیقاً مطابق مقادیر مجاز باشند.
- اطلاعات نامشخص را null قرار بده.
"""


SKIN_PATTERNS = {
    "Oily": r"چرب|oily",
    "Dry": r"خشک|dry",
    "Combination": r"مختلط|combination",
    "Sensitive": r"حساس|sensitive",
    "Dehydrated": r"کم\s*آب|کم‌آب|دهیدراته|dehydrated",
    "All skin types": r"همه\s*نوع\s*پوست|all skin types",
}


def detect_skin_type(history: list[dict], current_message: str):
    messages = [
        message.get("content", "")
        for message in history
        if message.get("role") == "user"
    ]
    messages.append(current_message)

    detected = None

    for message in messages:
        for skin_type, pattern in SKIN_PATTERNS.items():
            matches = list(re.finditer(pattern, message, re.IGNORECASE))

            for match in matches:
                before = message[max(0, match.start() - 20):match.start()]
                after = message[match.end():match.end() + 30]

                is_negated = bool(
                    re.search(
                        r"(نیست|نمی‌باشد|نمیباشد|ندارم|نیستم|not|isn't|is not)\s*$",
                        before,
                        re.IGNORECASE,
                    )
                    or re.match(
                        r"\s*(نیست|نمی‌باشد|نمیباشد|ندارم|نیستم|not)\b",
                        after,
                        re.IGNORECASE,
                    )
                )

                if is_negated:
                    if detected == skin_type:
                        detected = None
                else:
                    detected = skin_type

    return detected


class IntentExtractor:

    async def extract(
        self,
        user_message: str,
        conversation_history: list[dict] | None = None,
    ) -> dict:

        history = (conversation_history or [])[-20:]

        context = {
            "history": history,
            "current_message": user_message,
        }

        response = await ollama_client.chat(
            messages=[
                {"role": "system", "content": INTENT_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(context, ensure_ascii=False),
                },
            ],
            temperature=0,
        )

        content = response.get("message", {}).get("content", "")
        match = re.search(r"\{.*\}", content, re.DOTALL)

        if not match:
            raise ValueError(f"Invalid intent response: {content}")

        result = json.loads(match.group())

        if result.get("intent") not in {"search", "chat"}:
            raise ValueError("Invalid intent")

        allowed_categories = {
            "Sunscreen", "Cleanser", "Serum", "Foundation", None
        }

        if result.get("category") not in allowed_categories:
            result["category"] = None

        if not isinstance(result.get("min_spf"), int):
            result["min_spf"] = None

        if result["min_spf"] is not None:
            result["min_spf"] = max(0, min(result["min_spf"], 100))

        if not isinstance(result.get("query"), str):
            result["query"] = user_message

        if not isinstance(result.get("brand"), str):
            result["brand"] = None

        # نوع پوست از متن کاربران استخراج می‌شود، نه از حدس مدل
        detected_skin = detect_skin_type(history, user_message)
        if detected_skin:
            result["skin_type"] = detected_skin
        else:
            result["skin_type"] = None

        return result


intent_extractor = IntentExtractor()
