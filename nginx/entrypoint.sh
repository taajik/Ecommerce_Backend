#!/bin/sh
set -e

# Function to install openssl if not present
install_openssl() {
    if ! command -v openssl >/dev/null 2>&1; then
        apk add --no-cache openssl
    fi
}

CERT_DIR="/etc/nginx/ssl"
CERT_FILE="$CERT_DIR/self.crt"
KEY_FILE="$CERT_DIR/self.key"

# Generate self-signed certificate if doesn't exists
if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
    install_openssl
    mkdir -p "$CERT_DIR"

    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$KEY_FILE" \
        -out "$CERT_FILE" \
        -subj "/CN=localhost"

    chown -R 101:101 "$CERT_DIR"
    chmod 600 "$KEY_FILE"
    chmod 644 "$CERT_FILE"
fi
