import random
import string

def generate_email(cohort: str, name: str = "test", surname: str = "user") -> str:
    digits = ''.join(random.choices(string.digits, k=3))
    return f"{name}_{surname}_{cohort}_{digits}@yandex.ru"

def generate_password(length: int = 8) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))
