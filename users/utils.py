import random
import string

def get_random_code(length: int = 6) -> str:
    """
    Генерирует случайный цифровой код фиксированной длины.
    """
    return ''.join(random.choices(string.digits, k=length))
