lint:
    ruff format
    ruff check --fix
    mypy . --strict

clean:
    docker compose -f docker-compose.base.yaml down -v

run target build="" profile="":
    #!/usr/bin/env bash
    set -e

    BUILD_FLAG=""

    if [ "{{build}}" = "build" ]; then
        BUILD_FLAG="--build"
    fi

    PROFILE_FLAG=""

    if [ "{{profile}}" = "observability" ]; then
        PROFILE_FLAG="--profile observability"
    fi

    if [ "{{target}}" = "prod" ]; then
        docker compose \
            -f docker-compose.base.yaml \
            -f docker-compose.prod.yaml \
            $PROFILE_FLAG \
            up $BUILD_FLAG
    else
        docker compose \
            -f docker-compose.base.yaml \
            -f docker-compose.dev.yaml \
            $PROFILE_FLAG \
            up $BUILD_FLAG
    fi

restart target:
    docker compose -f docker-compose.base.yaml restart {{target}}

attach target:
    docker compose -f docker-compose.base.yaml exec -it {{target}} /bin/bash