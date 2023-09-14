from app.tools import is_valid_pwd, get_hash


def test_pwd_validation():
    assert is_valid_pwd("") is False
    assert is_valid_pwd("abc1") is True


def test_hash_func():
    assert get_hash("abc") == "900150983cd24fb0d6963f7d28e17f72"
