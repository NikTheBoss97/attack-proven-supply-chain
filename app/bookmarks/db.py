# Author: Nicola Antonello
"""One database connection per request (ADR-0006)."""

from collections.abc import Iterator
from typing import Annotated

import psycopg
from fastapi import Depends
from psycopg.rows import dict_row


def connection() -> Iterator[psycopg.Connection]:
    """Connect with libpq's PG* variables, and return rows as dicts.

    The transaction commits when the request succeeds and rolls back when it
    raises, and the connection is always closed.
    """
    with psycopg.connect(row_factory=dict_row) as conn:
        yield conn


# By default FastAPI closes a dependency after the response is sent. Closing it
# when the endpoint returns means a response is sent only after the commit.
Connection = Annotated[psycopg.Connection, Depends(connection, scope="function")]
