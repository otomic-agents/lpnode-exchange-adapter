#!/bin/bash
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <tag>"
    exit 1
fi
TAG=$1
echo "Building Docker image..."
docker build -t magicpigdocker/images:$TAG .
echo "Pushing Docker image..."
docker push magicpigdocker/images:$TAG

echo "Docker image magicpigdocker/images:$TAG has been built and pushed successfully."