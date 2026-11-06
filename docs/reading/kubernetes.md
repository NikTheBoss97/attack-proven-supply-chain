<!-- Author: Nicola Antonello -->

# Kubernetes

Running the service in a throwaway cluster, and checking what runs there. Part of the [reading list](README.md).

## Test clusters

- kind, [Quick Start: Loading an Image Into Your Cluster](https://kind.sigs.k8s.io/docs/user/quick-start/#loading-an-image-into-your-cluster) (kind documentation). Loading a locally built image into the cluster's nodes, and why a `latest` tag makes Kubernetes try to pull it anyway.
- kind, [Access kind cluster from a container outside of cluster](https://github.com/kubernetes-sigs/kind/issues/2148) (GitHub issue #2148). Why a container has to join kind's Docker network, and use the internal kubeconfig, to reach the cluster.
- Docker, [Host network driver](https://docs.docker.com/engine/network/drivers/host/) (Docker documentation). How a container can share the host's network, and why Docker Desktop makes that opt-in.

## Manifests

- kubeconform, [README](https://github.com/yannh/kubeconform) (GitHub). Validating manifests against the Kubernetes schemas, which it downloads by default, and the limits of what schema validation catches.
