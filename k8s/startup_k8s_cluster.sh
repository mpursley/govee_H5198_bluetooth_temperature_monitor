#!/bin/bash
set -e

CLUSTER_NAME="services"
IMAGE_NAME="govee-logger:local"

# Ensure we are running from the project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/.."

# Check if kind is installed
if ! command -v kind &> /dev/null; then
    echo "Error: 'kind' is not installed. Please install it first."
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "Error: 'kubectl' is not installed. Please install it first."
    exit 1
fi

echo "Creating Kubernetes cluster..."
if kind get clusters | grep -q "^$CLUSTER_NAME$"; then
    echo "Cluster $CLUSTER_NAME already exists."
else
    kind create cluster --name $CLUSTER_NAME --config k8s/kind-config.yaml
fi

echo "Building Docker image..."
docker build -t $IMAGE_NAME .

echo "Loading image into Kind cluster..."
kind load docker-image $IMAGE_NAME --name $CLUSTER_NAME

echo "Applying manifests..."
kubectl --context kind-$CLUSTER_NAME apply -f k8s/deployment.yaml

echo "Waiting for deployment to be ready..."
kubectl --context kind-$CLUSTER_NAME -n govee-logger wait --for=condition=available deployment/govee-logger --timeout=60s || echo "Wait timed out, check pods."

echo "Done! You can verify logs with:"
echo "kubectl --context kind-$CLUSTER_NAME -n govee-logger logs -l app=govee-logger -f"
