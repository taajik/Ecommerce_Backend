#!/usr/bin/env sh
set -e

psql -v ON_ERROR_STOP=1 --username $POSTGRES_USER <<EOSQL
    CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
    ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
    ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
    ALTER ROLE $DB_USER SET timezone TO 'UTC';
    CREATE DATABASE $DB_NAME OWNER $DB_USER;
EOSQL
