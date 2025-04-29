#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
  echo ".env file not found!"
  exit 1
fi

# Export variables from .env file
set -o allexport
source .env
set +o allexport

echo "Environment variables have been exported."
