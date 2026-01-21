#!/usr/bin/env sh
set -e

: '
# django and postgres development run without compose:
sudo docker run --name postgres --network ebproj -v pg_data:/var/lib/postgresql/data/ -v ./postgres/init/:/docker-entrypoint-initdb.d/ --env-file .env -d postgres:17
sudo docker run --name django --network ebproj -p8000:8000 -v .:/app --env DJANGO_SETTINGS_MODULE=core.settings.development --env-file .env -d djangoapp:localrun
sudo docker exec -it django python manage.py migrate
'


## In linux, run the script with sudo.

if [ "$1" = "down" ]
then
    docker compose down

elif [ "$1" = "prod" ]
then
    # Production
    docker compose -f docker-compose.yml up -d db
    sleep 5
    docker compose run --rm web python manage.py migrate --noinput
    docker compose -f docker-compose.yml up -d web

else
    # Development
    docker compose up -d db
    sleep 5
    docker compose run --rm web python manage.py migrate --noinput
    docker compose up -d web
fi
