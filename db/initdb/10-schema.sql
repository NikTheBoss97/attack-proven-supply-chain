-- Author: Nicola Antonello
-- The schema, owned by a role that cannot log in (ADR-0006).
REVOKE ALL ON DATABASE bookmarks FROM PUBLIC;
CREATE ROLE bookmarks_owner NOLOGIN;
CREATE SCHEMA app AUTHORIZATION bookmarks_owner;
SET ROLE bookmarks_owner;
CREATE TABLE app.users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  token_sha256 bytea NOT NULL UNIQUE CHECK (octet_length(token_sha256) = 32),
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE app.bookmarks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES app.users (id),
  url text NOT NULL CHECK (char_length(url) <= 2048),
  title text NOT NULL CHECK (char_length(title) BETWEEN 1 AND 300),
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX bookmarks_by_owner ON app.bookmarks (user_id, created_at DESC);
RESET ROLE;
