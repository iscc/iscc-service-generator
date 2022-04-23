#!/usr/bin/env bash
set -euo pipefail

###
### Configuration
###

APP_VERSION=0.2.0

# Set a secure secret key
# generate with: docker run --rm ghcr.io/iscc/iscc-service-generator python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
DJANGO_SECRET_KEY='foobar'

# Configure the domain where the service should be reachable here
ALLOWED_HOSTS='["generator.iscc.tld", "cloud.digitalocean.com"]'

# Configure all CSRF trusted origins here, including the main domain with protocols and possibly
# ports
CSRF_TRUSTED_ORIGINS='["https://generator.iscc.tld"]'

# Set this to false if you intend to run Django migrations manually
AUTO_MIGRATE='true'

# Database
DATABASE_URL='postgres://iscc_generator_service:foobar@hostname:port/iscc_generator_service'

# Spaces
AWS_S3_REGION_NAME='nyc3'
AWS_S3_ENDPOINT_URL="https://${AWS_S3_REGION_NAME}.digitaloceanspaces.com"
AWS_STORAGE_BUCKET_NAME='foobar' # Name of the space you created
AWS_ACCESS_KEY_ID='foobar'
AWS_SECRET_ACCESS_KEY='foobar'

###
### Configuration end
### The following code does not need to be changed! Be careful if you modify anything.
###

apt-get update

# Install Docker
apt-get install -y --no-install-recommends ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list >/dev/null

apt-get update

apt-get install -y --no-install-recommends docker-ce docker-ce-cli containerd.io

# Install docker compose
mkdir -p "/usr/local/lib/docker/cli-plugins"
curl -SL https://github.com/docker/compose/releases/download/v2.3.4/docker-compose-linux-x86_64 -o "/usr/local/lib/docker/cli-plugins/docker-compose"
chmod +x "/usr/local/lib/docker/cli-plugins/docker-compose"

# Create project environment
mkdir /iscc-service-generator
pushd /iscc-service-generator >/dev/null

{
    echo "DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY"
    echo "ALLOWED_HOSTS=$ALLOWED_HOSTS"
    echo "CSRF_TRUSTED_ORIGINS=$CSRF_TRUSTED_ORIGINS"
    echo "AUTO_MIGRATE=$AUTO_MIGRATE"
    echo "DATABASE_URL=$DATABASE_URL"
    echo "AWS_S3_REGION_NAME=$AWS_S3_REGION_NAME";
    echo "AWS_S3_ENDPOINT_URL=$AWS_S3_ENDPOINT_URL";
    echo "AWS_STORAGE_BUCKET_NAME=$AWS_STORAGE_BUCKET_NAME";
    echo "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID";
    echo "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY";
} >.env

cat <<EOF >docker-compose.yml
version: "3.8"

services:
  backend:
    image: ghcr.io/iscc/iscc-service-generator:$APP_VERSION
    restart: always
    init: true
    ports:
      - 0.0.0.0:80:8000
    environment:
      - DJANGO_SECRET_KEY
      - ALLOWED_HOSTS
      - CSRF_TRUSTED_ORIGINS
      - AUTO_MIGRATE
      - DATABASE_URL
      - DEFAULT_FILE_STORAGE=storages.backends.s3boto3.S3Boto3Storage
      - AWS_S3_REGION_NAME
      - AWS_S3_ENDPOINT_URL
      - AWS_STORAGE_BUCKET_NAME
      - AWS_ACCESS_KEY_ID
      - AWS_SECRET_ACCESS_KEY
EOF

docker compose up -d

popd >/dev/null
