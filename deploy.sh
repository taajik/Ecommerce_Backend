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

    printf "\nRunning migrate...\n"
    docker compose run --rm web python manage.py migrate --noinput
    printf "\nRunning collectstatic...\n"
    docker compose -f docker-compose.yml run --rm web python manage.py collectstatic --noinput
    docker compose -f docker-compose.yml up -d web

    if [ ! -f ./nginx/certs/self.crt ] || [ ! -f ./nginx/certs/self.key ]; then
        printf "\nGenerating self-signed certificate...\n"
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ./nginx/certs/self.key \
            -out ./nginx/certs/self.crt \
            -subj "/CN=localhost"
        docker run --rm -v ebproj_ssl_certs:/target -v ./nginx/certs:/source nginx:1.30.2-alpine sh -c "cp -r /source/. /target/ && chown -R 101:101 /target/"
    fi
    docker compose -f docker-compose.yml up -d nginx

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
