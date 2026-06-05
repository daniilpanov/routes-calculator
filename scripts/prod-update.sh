#!/usr/bin/env bash
set -e

GIT_REF="${1:-master}"
DOCKER_TAG="${2:-}"

if [ -z "$DOCKER_TAG" ]; then
    if [ -f .env ]; then
        DOCKER_TAG=$(grep -oP '^DOCKER_PROD_IMAGES_TAG="?\K[^"]+' .env || echo "latest")
    else
        DOCKER_TAG="latest"
    fi
fi

echo "=== Git ref: $GIT_REF ==="
echo "=== Docker tag: $DOCKER_TAG ==="

git fetch -p --tags

if git show-ref --verify --quiet "refs/tags/$GIT_REF"; then
    echo "=== Switching to tag: $GIT_REF ==="
    git checkout "tags/$GIT_REF"
else
    echo "=== Switching to branch: $GIT_REF ==="
    git checkout "$GIT_REF"
    git pull origin "$GIT_REF"
fi

export DOCKER_PROD_IMAGES_TAG="$DOCKER_TAG"

docker compose down
docker compose pull
docker compose -f docker-compose.migrate.yml pull
./scripts/prod-db-migrate.sh upgrade head
docker compose up -d
