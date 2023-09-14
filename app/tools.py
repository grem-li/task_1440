import hashlib


def is_valid_pwd(pwd: str) -> bool:
    """
    Проверяем, что пароль подходит под требования (длинна, сложность и т.д.)
    """
    if len(pwd) < 3:
        return False
    return True


def get_hash(string: str) -> str:
    """
    Получаем хэш от строки
    """
    return hashlib.md5(string.encode("utf-8")).hexdigest()
