lint:
    ruff format
    ruff check --fix
    mypy . --strict

clean:
    docker compose -f docker-compose.base.yaml down -v

up target build="" profile="":
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

down flag="":
    #!/usr/bin/env bash

    set -e

    FLAG=""

    if [ "{{flag}}" = "rm" ]; then
        FLAG="-v"
    fi

    docker compose -f docker-compose.base.yaml down $FLAG

keygen path="src/conode/infrastructure/credentials/":
    #!/usr/bin/env bash

    openssl genrsa -out {{path}}private.pem 4096
    openssl rsa \
    -in {{path}}private.pem \
    -pubout \
    -out {{path}}public.pem

test flag="":
    #!/usr/bin/env bash

    set -e

    FLAG=""

    if [ "{{flag}}" = "parallel" ]; then
        FLAG="-n auto"
    fi

    pytest . $FLAG

restart target:
    docker compose -f docker-compose.base.yaml restart {{target}}


attach target:
    docker compose -f docker-compose.base.yaml exec -it {{target}} /bin/bash