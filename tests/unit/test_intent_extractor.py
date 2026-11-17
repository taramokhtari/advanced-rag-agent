from app.agent.intent_extractor import detect_skin_type


def test_detect_dry_skin():
    assert detect_skin_type([], "پوستم خشکه") == "Dry"


def test_detect_oily_skin():
    assert detect_skin_type([], "پوستم چربه") == "Oily"


def test_detect_sensitive_skin():
    assert detect_skin_type([], "پوستم حساسه") == "Sensitive"


def test_ignore_greeting():
    assert detect_skin_type([], "سلام، خوبی؟") is None


def test_negated_skin_type():
    assert detect_skin_type([], "پوستم خشک نیست") is None


def test_update_skin_type():
    history = [{"role": "user", "content": "پوستم چربه"}]
    assert detect_skin_type(history, "اشتباه کردم، پوستم خشکه") == "Dry"


def test_clear_previous_skin_type():
    history = [{"role": "user", "content": "پوستم خشکه"}]
    assert detect_skin_type(history, "پوستم خشک نیست") is None


def test_keep_previous_skin_type():
    history = [{"role": "user", "content": "پوستم خشکه"}]
    assert detect_skin_type(history, "یک ضدآفتاب معرفی کن") == "Dry"
