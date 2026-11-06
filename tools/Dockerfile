# syntax=docker/dockerfile:1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e
# Author: Nicola Antonello
#
# The toolbox: every command-line tool this project runs, pinned to exact bytes
# (ADR-0008, ADR-0009). A tool whose project publishes a SHA-256 for its release
# is fetched with ADD --checksum; one that publishes none is copied from its
# official image by digest. tools/run.sh builds and runs this image.

# python:3.14-trixie, which already includes git
ARG BASE=python:3.14-trixie@sha256:1cef1664561971647b94fedf437145415991d4feeda09c81df12acfad8829cde

# docker CLI 29.9.3: Docker publishes no checksum for its static binary
FROM docker:29.9.3-cli@sha256:2357639ad1ea7d0194134bf3292622fd4e562483966ed674e5d7c945b5f3b28d AS docker-cli
# shellcheck v0.11.0: its release publishes no checksum
FROM koalaman/shellcheck:v0.11.0@sha256:61862eba1fcf09a484ebcc6feea46f1782532571a34ed51fedf90dd25f925a8d AS shellcheck

FROM ${BASE} AS fetch
WORKDIR /out
# kind v0.33.0: SHA-256 from kind-linux-amd64.sha256sum
ADD --checksum=sha256:aee6151561422756b764a4ae28e7f44cda5af5a9eead3cc9985112b1de8d8e0d \
    https://github.com/kubernetes-sigs/kind/releases/download/v0.33.0/kind-linux-amd64 kind
# kubectl v1.37.2: SHA-256 from kubectl.sha256, beside it on dl.k8s.io
ADD --checksum=sha256:c04487523e7aa7d1493f7808174c899db93d7a9cf57531420cd76b9bd415f8f4 \
    https://dl.k8s.io/release/v1.37.2/bin/linux/amd64/kubectl kubectl
# buildx v0.38.2, the version docker:29.9.3-cli ships: SHA-256 from checksums.txt
ADD --checksum=sha256:7992ec09413b80ff57ba4e081f56fc833d7bac1d5e71143c6c809e7e6065f6d6 \
    https://github.com/docker/buildx/releases/download/v0.38.2/buildx-v0.38.2.linux-amd64 docker-buildx
# hadolint v2.15.1: SHA-256 from checksums.sha256
ADD --checksum=sha256:c7187db94eeeeca956519a6af171adc31453941a1e777961f6e680f697c8c507 \
    https://github.com/hadolint/hadolint/releases/download/v2.15.1/hadolint-linux-x86_64 hadolint
# gitleaks v8.30.1: SHA-256 from gitleaks_8.30.1_checksums.txt
ADD --checksum=sha256:551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb \
    https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz gitleaks.tar.gz
# actionlint v1.7.12: SHA-256 from actionlint_1.7.12_checksums.txt
ADD --checksum=sha256:8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8 \
    https://github.com/rhysd/actionlint/releases/download/v1.7.12/actionlint_1.7.12_linux_amd64.tar.gz actionlint.tar.gz
# kubeconform v0.8.0: SHA-256 from CHECKSUMS
ADD --checksum=sha256:9bc2bffbf71f261128533edaf912153948b7ff238f9a531ae6d34466ec287883 \
    https://github.com/yannh/kubeconform/releases/download/v0.8.0/kubeconform-linux-amd64.tar.gz kubeconform.tar.gz
RUN tar -xzf gitleaks.tar.gz gitleaks \
 && tar -xzf actionlint.tar.gz actionlint \
 && tar -xzf kubeconform.tar.gz kubeconform

FROM ${BASE}
COPY --from=fetch --chmod=0755 /out/kind /out/kubectl /out/hadolint /out/gitleaks /out/actionlint /out/kubeconform /usr/local/bin/
COPY --from=fetch --chmod=0755 /out/docker-buildx /usr/local/libexec/docker/cli-plugins/docker-buildx
COPY --from=docker-cli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=shellcheck /bin/shellcheck /usr/local/bin/shellcheck
# pytest, httpx, pip-tools, ruff and zizmor, hash-locked (tools/requirements.in)
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --root-user-action=ignore --disable-pip-version-check \
      --require-hashes --only-binary :all: -r /tmp/requirements.txt \
 && rm /tmp/requirements.txt \
 && git config --system --add safe.directory /work
# Python leaves no __pycache__ directories in the mounted repository.
ENV PATH=/work/tools/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /work
