# Ecommerce Backend

Dockerized backend project for an e-commerce store implemented using Django and PostgreSQL.


## Set up

Django and PostgreSQL need some environment variables for their configuration.

To set them up, rename the [`.env.example`](/.env.example) file to `.env` and fill it with the right values.


## Run

After setting up the env file, use the deploy.sh script to run the project.
Depending on the environment:
```
# For production:
deploy.sh prod

# For Development:
deploy.sh dev
```
And to stop the project:
```
deploy.sh down
```

On linux systems, docker needs to be run with super user privileges:
```
sudo ./deploy.sh
```
