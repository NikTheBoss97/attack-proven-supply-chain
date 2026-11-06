-- Author: Nicola Antonello
-- The service's login role, with only the table privileges it needs (ADR-0006).
-- If BOOKMARKS_API_PASSWORD is unset, psql leaves :'api_password' as written,
-- the statement fails, and setup stops under ON_ERROR_STOP (ADR-0010).
\getenv api_password BOOKMARKS_API_PASSWORD
CREATE ROLE bookmarks_api LOGIN PASSWORD :'api_password';
GRANT CONNECT ON DATABASE bookmarks TO bookmarks_api;
GRANT USAGE ON SCHEMA app TO bookmarks_api;
GRANT SELECT, INSERT ON app.users TO bookmarks_api;
GRANT SELECT, INSERT, DELETE ON app.bookmarks TO bookmarks_api;
ALTER ROLE bookmarks_api SET search_path = app;
