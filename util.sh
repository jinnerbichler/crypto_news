#!/usr/bin/env bash

set -e    # Exit immediately if a command exits with a non-zero status.

if [ "$1" == "dev-setup" ]; then

    source ./private_dev.sh
    docker-compose up -d --build db corenlp
    docker-compose logs -f corenlp

elif [ "$1" == "start-local" ]; then

    eval $(docker-machine env -u)
    docker-compose up -d --build
    docker-compose logs -f corenlp scraper

elif [ "$1" == "stop-local" ]; then

    eval $(docker-machine env -u)
    docker-compose stop

elif [ "$1" == "deploy-prod" ]; then

    eval $(docker-machine env crypto-news)
    docker-compose up -d --build
    docker-compose logs -f

fi