# Author: Nicola Antonello
"""The API's errors: a status and a JSON body `{"error": code}` (ADR-0006)."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ApiError(Exception):
    def __init__(self, status: int, code: str, headers: dict[str, str] | None = None):
        super().__init__(code)
        self.status = status
        self.code = code
        self.headers = headers


def invalid_token() -> ApiError:
    return ApiError(401, "invalid_token", {"WWW-Authenticate": "Bearer"})


def bookmark_not_found() -> ApiError:
    """The same 404 for a bookmark that does not exist and for someone else's."""
    return ApiError(404, "bookmark_not_found")


def install(app: FastAPI) -> None:
    """Register the handler that turns an ApiError into its response."""

    @app.exception_handler(ApiError)
    async def handle(_request: Request, error: ApiError) -> JSONResponse:
        return JSONResponse(
            {"error": error.code}, status_code=error.status, headers=error.headers
        )
