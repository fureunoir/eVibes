# eVibes

![LOGO](core/docs/images/evibes-big.png)

eVibes is an eCommerce backend service built with Django. It’s designed for flexibility, making it ideal for various use
cases and learning Django skills. The project is easy to customize, allowing for straightforward editing and extension.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
- [Configuration](#configuration)
    - [Environment Variables](#environment-variables)
- [Usage](#usage)
- [Contact](#contact)

## Features

- **Modular Architecture**: Easily extend and customize the backend to fit your needs.
- **Dockerized Deployment**: Quick setup and deployment using Docker and Docker Compose.
- **Asynchronous Task Processing**: Integrated Celery workers and beat scheduler for background tasks.
- **GraphQL and REST APIs**: Supports both GraphQL and RESTful API endpoints.
- **Internationalization**: Multilingual support using modeltranslate.
- **Advanced Caching**: Utilizes Redis for caching and task queuing.
- **Security**: Implements JWT authentication and rate limiting.

## Getting Started

### Prerequisites

- Docker and Docker Compose installed on your machine.
- Python 3.12 if running locally without Docker.

### Installation

1. Clone the repository:

   ```bash
   git clone https://gitlab.com/wiseless.xyz/eVibes.git
   cd eVibes
   ```

2. Copy the example environment file and configure it.

3. Build and start the services:

   ```bash
   docker-compose up -d --build
   ```

   This command will build the Docker images and start all the services defined in the `docker-compose.yml` file.

## Configuration

### Dockerfile

Don't forget to change the
`RUN sed -i 's|https://deb.debian.org/debian|https://ftp.<locale>.debian.org/debian|g' /etc/apt/sources.list.d/debian.sources`

### Environment Variables

The project uses environment variables for configuration. Below is an example of the `.env` file:

```plaintext
PROJECT_NAME="eVibes"
FRONTEND_DOMAIN="evibes.com"
BASE_DOMAIN="evibes.com"
SENTRY_DSN=""
DEBUG=1

SECRET_KEY="SUPERSECRETKEY"
JWT_SIGNING_KEY="SUPERSECRETJWTSIGNINGKEY"

ALLOWED_HOSTS="localhost 127.0.0.1 evibes.com api.evibes.com b2b.evibes.com"
CSRF_TRUSTED_ORIGINS="http://api.localhost http://127.0.0.1 https://evibes.com https://api.evibes.com https://www.evibes.com https://b2b.evibes.com"
CORS_ALLOWED_ORIGINS="http://api.localhost http://127.0.0.1 https://evibes.com https://api.evibes.com https://www.evibes.com https://b2b.evibes.com"

POSTGRES_DB="evibes"
POSTGRES_USER="evibes_user"
POSTGRES_PASSWORD="SUPERSECRETPOSTGRESPASSWORD"

DBBACKUP_SFTP_HOST="Your SFTP backup host"
DBBACKUP_SFTP_USER="The username to use to log in to that host"
DBBACKUP_SFTP_PASS="The password to use to log in to that host"

ELASTIC_PASSWORD="SUPERSECRETELASTICPASSWORD"

REDIS_PASSWORD="SUPERSECRETREDISPASSWORD"

CELERY_BROKER_URL="redis://:SUPERSECRETREDISPASSWORD@redis:6379/0"
CELERY_RESULT_BACKEND="redis://:SUPERSECRETREDISPASSWORD@redis:6379/0"

FLOWER_USER=evibes
FLOWER_PASSWORD="SUPERSECRETFLOWERPASSWORD"

EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST="smtp.whatever.evibes.com"
EMAIL_PORT="465"
EMAIL_USE_TLS=0
EMAIL_USE_SSL=1
EMAIL_HOST_USER="your-email-user@whatever.evibes.com"
EMAIL_HOST_PASSWORD="SUPERSECRETEMAILHOSTPASSWORD"
EMAIL_FROM="your-email-user@whatever.evibes.com"

COMPANY_NAME="eVibes, Inc."
COMPANY_PHONE_NUMBER="+888888888888"
COMPANY_ADDRESS="The place that does not exist"

OPENAI_API_KEY="Haha, really?"

ABSTRACT_API_KEY="Haha, really? x2"
```

**Note**: Replace all placeholder values (e.g., `your-secret-key`, `your-database-name`) with your actual configuration.

## Usage

Add these lines to your hosts-file to use django-hosts functionality on localhost:

```hosts
127.0.0.1 api.localhost
127.0.0.1 b2b.localhost
```

Otherwise, add needed subdomains to DNS-settings of your domain.

Once the services are up and running, you can access the application at `http://api.localhost:8000`.

- **Django Admin**: `http://api.localhost:8000/admin/`
- **API Endpoints**:
    - REST API: `http://api.localhost:8000/docs/swagger` or `http://api.localhost:8000/docs/redoc`
    - GraphQL API: `http://api.localhost:8000/graphql/`

## Contact

- **Author**: Egor "fureunoir" Gorbunov
    - Email: contact@fureunoir.com
    - Telegram: [@fureunoir](https://t.me/fureunoir)

![FAVICON](core/docs/images/evibes.png)