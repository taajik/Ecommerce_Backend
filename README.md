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


## SSL Certificate

After you run the project for production, run this command to get a SSL certificate form Let's Encrypt:

(replace the -d and --email values with your domain name and email)
```
docker compose run --rm certbot certonly --webroot --webroot-path=/var/www/ebproj/certbot -d EXAMPLE.COM -d www.EXAMPLE.COM --email YOU@GMAIL.COM --agree-tos --no-eff-email
```

And if successful, restart nginx:
```
docker compose restart nginx
```

Also, set up a cron job for certificate renewal:
```
0 3 * * * docker compose run --rm certbot renew -q && docker compose exec nginx nginx -s reload
```
