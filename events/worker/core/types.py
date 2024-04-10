from typing import Annotated

from email_validator import validate_email
from pydantic import AfterValidator


def is_valid_email(email: str) -> str:
    """Validate string as an email"""
    emailinfo = validate_email(email, check_deliverability=False)
    return emailinfo.normalized


EmailType = Annotated[str, AfterValidator(is_valid_email)]
