def normalize_skin_type(value: str | None) -> str | None:
    if not value:
        return None

    value = value.strip().lower()

    aliases = {
        "چرب": "Oily",
        "چربه": "Oily",
        "پوست چرب": "Oily",
        "خشک": "Dry",
        "پوست خشک": "Dry",
        "مختلط": "Combination",
        "پوست مختلط": "Combination",
        "حساس": "Sensitive",
        "پوست حساس": "Sensitive",
        "دهیدراته": "Dehydrated",
        "کم آب": "Dehydrated",
        "همه انواع پوست": "All skin types",
    }

    return aliases.get(value, value)


def normalize_category(value: str | None) -> str | None:
    if not value:
        return None

    value = value.strip().lower()

    aliases = {
        "ضد آفتاب": "Sunscreen",
        "ضدآفتاب": "Sunscreen",
        "شوینده": "Cleanser",
        "سرم": "Serum",
        "کرم پودر": "Foundation",
    }

    return aliases.get(value, value)
