# Author: Nicola Antonello
"""The bookmarks API's endpoints (ADR-0004, ADR-0006)."""

from fastapi import FastAPI

from bookmarks import auth, errors, store
from bookmarks.db import Connection

app = FastAPI(title="bookmarks")
errors.install(app)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Answer Kubernetes' probes without touching the database."""
    return {"status": "ok"}


@app.post("/users", status_code=201)
def create_user(conn: Connection) -> dict[str, str]:
    """Create a user and return its token, the only time it is ever shown."""
    token = auth.new_token()
    user_id = store.create_user(conn, auth.token_digest(token))
    return {"id": str(user_id), "token": token}
