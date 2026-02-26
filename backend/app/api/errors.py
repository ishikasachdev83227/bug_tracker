from fastapi import HTTPException, status


def api_error(
    status_code: int,
    code: str,
    message: str,
    details: dict | list | None = None,
) -> HTTPException:
    payload: dict = {"error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return HTTPException(status_code=status_code, detail=payload)


def unauthorized(message: str = "Unauthorized") -> HTTPException:
    return api_error(status.HTTP_401_UNAUTHORIZED, "unauthorized", message)
