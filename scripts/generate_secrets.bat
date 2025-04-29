@echo off
setlocal EnableDelayedExpansion

REM Static values
set "PROJECT_NAME=eVibes"
set "FRONTEND_DOMAIN=evibes.com"
set "BASE_DOMAIN=evibes.com"
set "SENTRY_DSN="
set "DEBUG=1"

set "ALLOWED_HOSTS=localhost 127.0.0.1 evibes.com api.evibes.com b2b.evibes.com"
set "CSRF_TRUSTED_ORIGINS=http://api.localhost http://127.0.0.1 https://evibes.com https://api.evibes.com https://www.evibes.com https://b2b.evibes.com"
set "CORS_ALLOWED_ORIGINS=http://api.localhost http://127.0.0.1 https://evibes.com https://api.evibes.com https://www.evibes.com https://b2b.evibes.com"

set "POSTGRES_DB=evibes"
set "POSTGRES_USER=evibes_user"

set "EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend"
set "EMAIL_HOST=smtp.whatever.evibes.com"
set "EMAIL_PORT=465"
set "EMAIL_USE_TLS=0"
set "EMAIL_USE_SSL=1"
set "EMAIL_HOST_USER=your-email-user@whatever.evibes.com"
set "EMAIL_FROM=your-email-user@whatever.evibes.com"

set "COMPANY_NAME=eVibes, Inc."
set "COMPANY_PHONE_NUMBER=+888888888888"
set "COMPANY_ADDRESS=The place that does not exist"

REM Function to generate a random hex string via PowerShell
for /f "usebackq tokens=*" %%A in (`powershell -NoProfile -Command ^
  "[System.Convert]::ToHexString((New-Object Byte[] %1 | %%{ Get-Random -Maximum 256 }))"`) do set "RAND_HEX=%%A"

call :gen 32 SECRET_KEY
call :gen 64 JWT_SIGNING_KEY
call :gen 16 POSTGRES_PASSWORD
call :gen 16 ELASTIC_PASSWORD
call :gen 16 REDIS_PASSWORD
call :gen 16 FLOWER_PASSWORD
call :gen 16 EMAIL_HOST_PASSWORD
call :gen 32 OPENAI_API_KEY
call :gen 32 ABSTRACT_API_KEY

REM Write .env
(
echo PROJECT_NAME="%PROJECT_NAME%"
echo FRONTEND_DOMAIN="%FRONTEND_DOMAIN%"
echo BASE_DOMAIN="%BASE_DOMAIN%"
echo SENTRY_DSN="%SENTRY_DSN%"
echo DEBUG=%DEBUG%
echo.
echo SECRET_KEY="%SECRET_KEY%"
echo JWT_SIGNING_KEY="%JWT_SIGNING_KEY%"
echo.
echo ALLOWED_HOSTS="%ALLOWED_HOSTS%"
echo CSRF_TRUSTED_ORIGINS="%CSRF_TRUSTED_ORIGINS%"
echo CORS_ALLOWED_ORIGINS="%CORS_ALLOWED_ORIGINS%"
echo.
echo POSTGRES_DB="%POSTGRES_DB%"
echo POSTGRES_USER="%POSTGRES_USER%"
echo POSTGRES_PASSWORD="%POSTGRES_PASSWORD%"
echo.
echo ELASTIC_PASSWORD="%ELASTIC_PASSWORD%"
echo.
echo REDIS_PASSWORD="%REDIS_PASSWORD%"
echo.
echo CELERY_BROKER_URL="redis://:%REDIS_PASSWORD%@redis:6379/0"
echo CELERY_RESULT_BACKEND="redis://:%REDIS_PASSWORD%@redis:6379/0"
echo.
echo FLOWER_USER=evibes
echo FLOWER_PASSWORD="%FLOWER_PASSWORD%"
echo.
echo EMAIL_BACKEND="%EMAIL_BACKEND%"
echo EMAIL_HOST="%EMAIL_HOST%"
echo EMAIL_PORT="%EMAIL_PORT%"
echo EMAIL_USE_TLS=%EMAIL_USE_TLS%
echo EMAIL_USE_SSL=%EMAIL_USE_SSL%
echo EMAIL_HOST_USER="%EMAIL_HOST_USER%"
echo EMAIL_HOST_PASSWORD="%EMAIL_HOST_PASSWORD%"
echo EMAIL_FROM="%EMAIL_FROM%"
echo.
echo COMPANY_NAME="%COMPANY_NAME%"
echo COMPANY_PHONE_NUMBER="%COMPANY_PHONE_NUMBER%"
echo COMPANY_ADDRESS="%COMPANY_ADDRESS%"
echo.
echo OPENAI_API_KEY="%OPENAI_API_KEY%"
echo.
echo ABSTRACT_API_KEY="%ABSTRACT_API_KEY%"
) > .env

echo .env file generated with fresh secrets.
goto :eof

:gen
REM %1 = number of bytes; %2 = variable name
for /f "usebackq tokens=*" %%A in (`powershell -NoProfile -Command ^
  "[System.Convert]::ToHexString((New-Object Byte[] %1 | %%{ Get-Random -Maximum 256 }))"`) do set "%2=%%A"
goto :eof