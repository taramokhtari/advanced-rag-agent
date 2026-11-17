PRODUCT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "hybrid_search_products",
            "description": (
                "Search beauty products using PostgreSQL and ChromaDB. "
                "Use this tool only when the customer explicitly requests product search, recommendations, or comparison. Do not use it merely because the customer shares personal preferences. "
                "Extract skin type and product category from the customer request. "
                "Never translate enum values. Use only the exact allowed values."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Customer request in its original language."
                    },
                    "skin_type": {
                        "type": ["string", "null"],
                        "enum": [
                            "Oily",
                            "Dry",
                            "Combination",
                            "Sensitive",
                            "Dehydrated",
                            "All skin types",
                            None
                        ],
                        "description": (
                            "Use Oily for چرب, Dry for خشک, "
                            "Combination for مختلط, Sensitive for حساس, "
                            "Dehydrated for کم‌آب. "
                            "Use null if the customer did not specify skin type."
                        )
                    },
                    "category": {
                        "type": ["string", "null"],
                        "enum": [
                            "Sunscreen",
                            "Cleanser",
                            "Serum",
                            "Foundation",
                            None
                        ],
                        "description": (
                            "Use Sunscreen for ضدآفتاب, Cleanser for شوینده, "
                            "Serum for سرم, Foundation for کرم پودر. "
                            "Use null if unspecified."
                        )
                    },
                    "brand": {
                        "type": ["string", "null"],
                        "description": "Brand name if explicitly specified; otherwise null."
                    },
                    "min_spf": {
                        "type": ["integer", "null"],
                        "description": "Minimum SPF required, or null if unspecified."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results. Default 5."
                    }
                },
                "required": ["query"]
            }
        }
    }
]
