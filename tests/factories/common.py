import random
import string


def generate_random_string(
    length: int = 10,
    *,
    include_lowercase: bool = True,
    include_uppercase: bool = True,
    include_digits: bool = True,
    include_special_symbols: bool = True,
) -> str:
    include_range: list[str] = []

    if include_lowercase:
        include_range.extend(string.ascii_lowercase)
    if include_uppercase:
        include_range.extend(string.ascii_uppercase)
    if include_digits:
        include_range.extend(string.digits)
    if include_special_symbols:
        include_range.extend(string.punctuation)

    return "".join([random.choice(include_range) for _ in range(length)])


def generate_random_ip() -> str:
    return ".".join([str(random.randint(1, 255)) for _ in range(4)])
