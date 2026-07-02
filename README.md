# Ecommerce Backend

Dockerized backend project for an e-commerce store implemented using Django, PostgreSQL and Nginx.


## Setup


You need to set up some environment variables for project configuration.

To do so, rename the [`.env.example`](/.env.example) file to `.env` and fill it with the right values.


## Run

Depending on the environment, you can run the project like this:
```
# For Production:
docker compose up -d

# For Development:
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```
