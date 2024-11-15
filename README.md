# eVibes

eVibes is an open-source eCommerce backend service built with Django. It’s designed for flexibility, making it ideal for various use cases and learning Django skills. The project is easy to customize, allowing for straightforward editing and extension.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
- [Configuration](#configuration)
    - [Environment Variables](#environment-variables)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **Modular Architecture**: Easily extend and customize the backend to fit your needs.
- **Dockerized Deployment**: Quick setup and deployment using Docker and Docker Compose.
- **Asynchronous Task Processing**: Integrated Celery workers and beat scheduler for background tasks.
- **GraphQL and REST APIs**: Supports both GraphQL and RESTful API endpoints.
- **Internationalization**: Multilingual support using django-parler.
- **Advanced Caching**: Utilizes Redis for caching and task queuing.
- **Security**: Implements JWT authentication and rate limiting.

## Getting Started

### Prerequisites

- Docker and Docker Compose installed on your machine.
- Python 3.12 if running locally without Docker.

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/fureunoir/evibes.git
   cd evibes
   ```

2. Copy the example environment file and configure it.

3. Build and start the services:

   ```bash
   docker-compose up -d --build
   ```

   This command will build the Docker images and start all the services defined in the `docker-compose.yml` file.

## Configuration

### Environment Variables

The project uses environment variables for configuration. Below is an example of the `.env` file:

```plaintext
PROJECT_NAME="eVibes"
FRONTEND_DOMAIN="app.evibes.com"
BASE_DOMAIN="evibes.com"
SENTRY_DSN=""
DEBUG=1

SECRET_KEY="your-secret-key"
JWT_SIGNING_KEY="your-jwt-signing-key"

ALLOWED_HOSTS="localhost 127.0.0.1 evibes.com api.evibes.com"
CSRF_TRUSTED_ORIGINS="http://localhost:8000 http://127.0.0.1:8000 https://api.evibes.com"
CORS_ALLOWED_ORIGINS="http://localhost http://127.0.0.1 https://evibes.com https://api.evibes.com"

POSTGRES_DB="your-database-name"
POSTGRES_USER="your-database-user"
POSTGRES_PASSWORD="your-database-password"

TELEGRAM_TOKEN="your-telegram-token"

CASHIER_SHOP_ID=""
CASHIER_URL=""
CASHIER_SECRET_KEY=""
EXCHANGE_RATE_API_KEY="your-exchange-rate-api-key"

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST="smtp.example.com"
EMAIL_PORT="587"
EMAIL_USE_TLS=1
EMAIL_USE_SSL=0
EMAIL_HOST_USER="your-email@example.com"
EMAIL_HOST_PASSWORD="your-email-password"

COMPANY_NAME="eVibes"
COMPANY_PHONE_NUMBER="+1234567890"
COMPANY_ADDRESS="Your Company Address"

OPENAI_API_KEY="your-openai-api-key"

ABSTRACT_API_KEY="your-abstract-api-key"
```

**Note**: Replace all placeholder values (e.g., `your-secret-key`, `your-database-name`) with your actual configuration.

## Usage

Add these lines to your hosts-file to use django-hosts functionality on localhost:
```hosts
127.0.0.1 api.localhost
127.0.0.1 b2b.localhost
```

Otherwise add needed subdomains to DNS-settings of your domain.

Once the services are up and running, you can access the application at `http://api.localhost:8000`.

- **Django Admin**: `http://api.localhost:8000/admin/`
- **API Endpoints**:
    - REST API: `http://api.localhost:8000/api/`
    - GraphQL API: `http://api.localhost:8000/graphql/`

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for review.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Contact

- **Author**: Egor "fureunoir" Gorbunov
    - Email: contact@fureunoir.com
    - Telegram: [@fureunoir](https://t.me/fureunoir)

eVibes is an open-source project aimed at providing a flexible and customizable eCommerce backend solution. Your contributions and support are greatly appreciated!