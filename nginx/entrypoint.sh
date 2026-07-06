#!/bin/sh
set -e


# Function to install openssl if not present
install_openssl() {
    if ! command -v openssl >/dev/null 2>&1; then
        apk add --no-cache openssl
    fi
}


DOMAIN="${SERVER_NAMES%% *}"

CERT_DIR="/etc/nginx/ssl"
CERT_FILE="$CERT_DIR/fullchain.pem"
KEY_FILE="$CERT_DIR/privkey.pem"

CERTBOT_CERT_DIR="/etc/letsencrypt/live/${DOMAIN}"
CERTBOT_CERT_FILE="$CERTBOT_CERT_DIR/fullchain.pem"
CERTBOT_KEY_FILE="$CERTBOT_CERT_DIR/privkey.pem"

mkdir -p "$CERT_DIR"


# Replace self-signed certificates with the ones certbot has created.
if [ -f "$CERTBOT_CERT_FILE" ] && [ -f "$CERTBOT_KEY_FILE" ] && [ ! -L "$CERT_FILE" ] && [ ! -L "$KEY_FILE" ]; then
    ln -sf $CERTBOT_CERT_FILE $CERT_FILE
    ln -sf $CERTBOT_KEY_FILE $KEY_FILE
fi

# Generate self-signed certificate if none exists
if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
    install_openssl

    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$KEY_FILE" \
        -out "$CERT_FILE" \
        -subj "/CN=${DOMAIN}"

    chown -R 101:101 "$CERT_DIR"
    chmod 600 "$KEY_FILE"
    chmod 644 "$CERT_FILE"
fi
