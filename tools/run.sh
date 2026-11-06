#!/bin/sh
# Author: Nicola Antonello
#
# Runs a command in the toolbox image, the same way on any machine with Docker
# (ADR-0008, ADR-0009):
#   tools/run.sh <command> [args...]
# The repository is mounted at /work, and so is the Docker socket, which kind
# needs. Whatever runs here controls the host's Docker, so run only code you trust.
set -eu

repo=$(cd "$(dirname "$0")/.." && pwd)
case "$(uname -s)" in
  MINGW* | MSYS*)
    # Git Bash rewrites arguments that look like paths unless told not to, and
    # Docker Desktop needs the repository as a Windows path.
    export MSYS_NO_PATHCONV=1
    repo=$(cd "$repo" && pwd -W)
    ;;
esac

image=$(docker build --platform linux/amd64 -q -t apsc-toolbox "$repo/tools")
name="apsc-toolbox-$$"
exec docker run --rm --init --platform linux/amd64 \
  --name "$name" --env TOOLBOX_CONTAINER="$name" \
  --volume "$repo:/work" --workdir /work \
  --volume /var/run/docker.sock:/var/run/docker.sock \
  "$image" "$@"
