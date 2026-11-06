# Author: Nicola Antonello
# PostgreSQL 18, rebuilt here from a pinned upstream digest (ADR-0005), which
# creates the schema and the service's two roles on its first start (ADR-0006).
FROM postgres:18-trixie@sha256:bd5dfa494a5a259704365813dbfa5fa6b3e69be7348d43b547f540c730478583
COPY initdb/ /docker-entrypoint-initdb.d/
USER 999:999
