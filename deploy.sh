#!/usr/bin/env sh
set -e

## In linux, run the script with sudo.


if [ "$1" = "down" ]
then
    docker compose down

elif [ "$1" = "prod" ]
then
    ## Production
    docker compose -f docker-compose.yml up -d db
    sleep 5
    docker compose run --rm web python manage.py migrate --noinput
    docker compose -f docker-compose.yml up -d web

elif [ "$1" = "dev" ] || [ -z "$1" ]
then
    ## Development
    docker compose up -d db
    sleep 5
    docker compose run --rm web python manage.py migrate --noinput
    docker compose up -d web

else
    printf "usage: deploy.sh COMMAND\n"
    printf "linux: sudo ./deploy.sh COMMAND\n"
    printf "\nTo start:\n"
    printf "  deploy.sh dev     For development environment\n"
    printf "  deploy.sh prod    For production environment\n"
    printf "\nTo stop:\n"
    printf "  deploy.sh down\n"
fi




: '
# django and postgres development run without compose:
sudo docker run --name postgres --network ebproj -v pg_data:/var/lib/postgresql/data/ -v ./postgres/init/:/docker-entrypoint-initdb.d/ --env-file .env -d postgres:17
sudo docker run --name django --network ebproj -p8000:8000 -v .:/app --env DJANGO_SETTINGS_MODULE=config.settings.development --env-file .env -d djangoapp:localrun
sudo docker exec -it django python manage.py migrate
'
