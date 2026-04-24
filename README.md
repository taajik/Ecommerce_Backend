# Ecommerce Backend

Dockerized backend project for an e-commerce store implemented using Django and PostgreSQL.


## Run

Use the deploy.sh script to run the project. Depending on the environment:
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
