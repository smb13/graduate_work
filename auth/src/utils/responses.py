from http import HTTPStatus

from fastapi import HTTPException

invalid_credentials = HTTPException(
    status_code=HTTPStatus.UNAUTHORIZED,
    detail="Invalid authentication credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
