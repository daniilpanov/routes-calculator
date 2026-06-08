#!/usr/bin/env bash
set -e

GIT_REF="${1:-master}"
DOCKER_TAG="${2:-}"
TAG_MESSAGE="${3:-}"

if [ -z "$DOCKER_TAG" ]; then
    if [ -f .env ]; then
        DOCKER_TAG=$(grep -oP '^DOCKER_PROD_IMAGES_TAG="?\K[^"]+' .env || echo "latest")
    else
        DOCKER_TAG="latest"
    fi
else
    echo "=== Updating .env DOCKER_PROD_IMAGES_TAG to $DOCKER_TAG ==="
    if [ -f .env ]; then
        if grep -qP '^DOCKER_PROD_IMAGES_TAG=' .env; then
            sed -i 's/^DOCKER_PROD_IMAGES_TAG=.*/DOCKER_PROD_IMAGES_TAG="'"$DOCKER_TAG"'"/' .env
        else
            echo 'DOCKER_PROD_IMAGES_TAG="'"$DOCKER_TAG"'"' >> .env
        fi
    else
        echo 'DOCKER_PROD_IMAGES_TAG="'"$DOCKER_TAG"'"' > .env
    fi
fi

echo "=== Git ref: $GIT_REF ==="
echo "=== Docker tag: $DOCKER_TAG ==="

git fetch -p --tags

if git show-ref --verify --quiet "refs/tags/$GIT_REF"; then
    echo "=== Switching to tag: $GIT_REF ==="
    git checkout "$GIT_REF"
elif git show-ref --verify --quiet "refs/heads/$GIT_REF"; then
    echo "=== Switching to branch: $GIT_REF ==="
    git checkout "$GIT_REF"
    git pull origin "$GIT_REF"
else
    echo "=== Creating and pushing git tag '$GIT_TAG' with message '$TAG_MESSAGE' from 'master' ==="
    git checkout master

    if [ -n "$TAG_MESSAGE" ]; then
      git tag -a "$GIT_REF" -m "$TAG_MESSAGE"
    else
      git tag "$GIT_REF"
    fi

    git push origin "$GIT_REF"
fi

export DOCKER_PROD_IMAGES_TAG="$DOCKER_TAG"

docker compose down
docker compose pull
docker compose -f docker-compose.migrate.yml pull
./scripts/prod-db-migrate.sh upgrade head
docker compose up -d
