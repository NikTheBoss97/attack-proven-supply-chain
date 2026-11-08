# Author: Nicola Antonello
# The bookmarks API (ADR-0004, ADR-0006). Three targets: base holds the runtime
# packages, test adds the tests, and runtime comes last, so it is the default.
FROM python:3.14-slim-trixie@sha256:af8a5aa14780025dbfbcfbc81bd8a91ebd87711dd5b0f48ed71090949dd7cb1d AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir --root-user-action=ignore --disable-pip-version-check \
      --require-hashes --only-binary :all: -r requirements.txt

FROM base AS test
COPY requirements-test.txt .
RUN pip install --no-cache-dir --root-user-action=ignore --disable-pip-version-check \
      --require-hashes --only-binary :all: -r requirements-test.txt
COPY bookmarks/ bookmarks/
COPY tests/ tests/
USER 10001:10001
CMD ["python", "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"]

FROM base AS runtime
COPY bookmarks/ bookmarks/
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "bookmarks.main:app", "--host", "0.0.0.0", "--port", "8000"]
