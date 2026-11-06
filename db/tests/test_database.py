# Author: Nicola Antonello
"""The database's two roles, and what the service's role may do (ADR-0006)."""

from conftest import psql, sql


def test_api_role_logs_in_with_its_password():
    assert sql("SELECT current_user") == "bookmarks_api"


def test_api_role_rejects_a_wrong_password():
    result = psql("SELECT 1", password="wrong")
    assert result.returncode != 0
    assert "password authentication failed" in result.stderr


def test_api_role_has_no_special_attributes():
    attributes = sql(
        "SELECT rolsuper, rolcreaterole, rolcreatedb, rolbypassrls, rolreplication"
        " FROM pg_roles WHERE rolname = current_user"
    )
    assert attributes == "f|f|f|f|f"


def test_tables_belong_to_the_owner_role():
    owners = sql(
        "SELECT string_agg(tablename || ':' || tableowner, ',' ORDER BY tablename)"
        " FROM pg_tables WHERE schemaname = 'app'"
    )
    assert owners == "bookmarks:bookmarks_owner,users:bookmarks_owner"


def test_api_role_has_exactly_the_privileges_it_needs():
    grants = sql(
        "SELECT string_agg(table_name || ':' || privilege_type, ','"
        " ORDER BY table_name, privilege_type)"
        " FROM information_schema.role_table_grants WHERE grantee = 'bookmarks_api'"
    )
    assert grants == (
        "bookmarks:DELETE,bookmarks:INSERT,bookmarks:SELECT,users:INSERT,users:SELECT"
    )


def test_api_role_cannot_create_tables():
    result = psql("CREATE TABLE app.probe (id int)")
    assert "permission denied for schema app" in result.stderr


def test_api_role_cannot_run_server_programs():
    result = psql("COPY (SELECT 1) TO PROGRAM 'true'")
    assert "COPY to or from an external program" in result.stderr
