# app/utils/helpers.py
import secrets
import string
import re


def generate_ticket_code(length: int = 12) -> str:
    """
    Generate a unique ticket code.

    Format: CINE-XXXXXXXX (where X is alphanumeric)

    Args:
        length: Length of the random part (default 8)

    Returns:
        Unique ticket code string
    """
    characters = string.ascii_uppercase + string.digits
    random_part = ''.join(secrets.choice(characters) for _ in range(length - 5))
    return f"CINE-{random_part}"


def validate_email(email: str) -> bool:
    """
    Validate email format using regex.

    Args:
        email: Email string to validate

    Returns:
        True if valid email format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate Colombian phone number format.
    Accepts formats like: +57XXXXXXXXXX, 57XXXXXXXXXX, 3XXXXXXXXX

    Args:
        phone: Phone string to validate

    Returns:
        True if valid Colombian phone format, False otherwise
    """
    # Remove spaces and dashes
    clean_phone = re.sub(r'[\s-]', '', phone)

    # Colombian phone patterns
    patterns = [
        r'^\+57[39]\d{9}$',  # +573XXXXXXXXX or +579XXXXXXXXX
        r'^57[39]\d{9}$',  # 573XXXXXXXXX or 579XXXXXXXXX
        r'^[39]\d{9}$',  # 3XXXXXXXXX or 9XXXXXXXXX
    ]

    return any(bool(re.match(pattern, clean_phone)) for pattern in patterns)


def format_currency(amount: float, currency: str = "COP") -> str:
    """
    Format currency amount for display.

    Args:
        amount: Amount to format
        currency: Currency code (default COP for Colombian Pesos)

    Returns:
        Formatted currency string
    """
    if currency == "COP":
        return f"${amount:,.0f} COP"
    return f"{amount:,.2f} {currency}"


def mask_card_number(card_number: str) -> str:
    """
    Mask credit card number for security.
    Shows only last 4 digits.

    Args:
        card_number: Credit card number string

    Returns:
        Masked card number (e.g., "**** **** **** 1234")
    """
    if len(card_number) < 4:
        return "****"

    last_four = card_number[-4:]
    return f"**** **** **** {last_four}"


def validate_movie_rating(rating: str) -> bool:
    """
    Validate movie rating according to MPAA standards.

    Args:
        rating: Movie rating string

    Returns:
        True if valid rating, False otherwise
    """
    valid_ratings = ["G", "PG", "PG-13", "R", "NC-17"]
    return rating.upper() in valid_ratings


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.

    Args:
        text: Text to convert to slug

    Returns:
        URL-friendly slug string
    """
    # Convert to lowercase and replace spaces with dashes
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')
