#!/usr/bin/env bash
set -euo pipefail

# Static values
PROJECT_NAME="eVibes"
FRONTEND_DOMAIN="evibes.com"
BASE_DOMAIN="evibes.com"
SENTRY_DSN=""
DEBUG=1

ALLOWED_HOSTS="localhost 127.0.0.1 evibes.com api.evibes.com b2b.evibes.com"
CSRF_TRUSTED_ORIGINS="http://api.localhost http://127.0.0.1 https://evibes.com https://api.evibes.com https://www.evibes.com https://b2b.evibes.com"
CORS_ALLOWED_ORIGINS="http://api.localhost http://127.0.0.1 https://evibes.com https://api.evibes.com https://www.evibes.com https://b2b.evibes.com"

POSTGRES_DB="evibes"
POSTGRES_USER="evibes_user"

EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST="smtp.whatever.evibes.com"
EMAIL_PORT="465"
EMAIL_USE_TLS=0
EMAIL_USE_SSL=1
EMAIL_HOST_USER="your-email-user@whatever.evibes.com"
EMAIL_FROM="your-email-user@whatever.evibes.com"

COMPANY_NAME="eVibes, Inc."
COMPANY_PHONE_NUMBER="+888888888888"
COMPANY_ADDRESS="The place that does not exist"

# Generate random secrets (hex strings)
rand_hex() {
  # $1 = number of bytes
  openssl rand -hex "$1"
}

SECRET_KEY="$(rand_hex 32)"
JWT_SIGNING_KEY="$(rand_hex 64)"
POSTGRES_PASSWORD="$(rand_hex 16)"
ELASTIC_PASSWORD="$(rand_hex 16)"
REDIS_PASSWORD="$(rand_hex 16)"
FLOWER_PASSWORD="$(rand_hex 16)"
EMAIL_HOST_PASSWORD="$(rand_hex 16)"
OPENAI_API_KEY="$(rand_hex 32)"
ABSTRACT_API_KEY="$(rand_hex 32)"

# Write .env
cat > .env <<EOF
PROJECT_NAME="${PROJECT_NAME}"
FRONTEND_DOMAIN="${FRONTEND_DOMAIN}"
BASE_DOMAIN="${BASE_DOMAIN}"
SENTRY_DSN="${SENTRY_DSN}"
DEBUG=${DEBUG}

SECRET_KEY="${SECRET_KEY}"
JWT_SIGNING_KEY="${JWT_SIGNING_KEY}"

ALLOWED_HOSTS="${ALLOWED_HOSTS}"
CSRF_TRUSTED_ORIGINS="${CSRF_TRUSTED_ORIGINS}"
CORS_ALLOWED_ORIGINS="${CORS_ALLOWED_ORIGINS}"

POSTGRES_DB="${POSTGRES_DB}"
POSTGRES_USER="${POSTGRES_USER}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD}"

ELASTIC_PASSWORD="${ELASTIC_PASSWORD}"

REDIS_PASSWORD="${REDIS_PASSWORD}"

CELERY_BROKER_URL="redis://:${REDIS_PASSWORD}@redis:6379/0"
CELERY_RESULT_BACKEND="redis://:${REDIS_PASSWORD}@redis:6379/0"

FLOWER_USER=evibes
FLOWER_PASSWORD="${FLOWER_PASSWORD}"

EMAIL_BACKEND="${EMAIL_BACKEND}"
EMAIL_HOST="${EMAIL_HOST}"
EMAIL_PORT="${EMAIL_PORT}"
EMAIL_USE_TLS=${EMAIL_USE_TLS}
EMAIL_USE_SSL=${EMAIL_USE_SSL}
EMAIL_HOST_USER="${EMAIL_HOST_USER}"
EMAIL_HOST_PASSWORD="${EMAIL_HOST_PASSWORD}"
EMAIL_FROM="${EMAIL_FROM}"

COMPANY_NAME="${COMPANY_NAME}"
COMPANY_PHONE_NUMBER="${COMPANY_PHONE_NUMBER}"
COMPANY_ADDRESS="${COMPANY_ADDRESS}"

OPENAI_API_KEY="${OPENAI_API_KEY}"

ABSTRACT_API_KEY="${ABSTRACT_API_KEY}"
EOF

echo ".env file generated with fresh secrets."
