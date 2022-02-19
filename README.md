# ISCC Generator - Web Service

**A microservice with REST API and management dashboard for generating ISCC codes**

## Development Status

Under development ...

# Development Quickstart

Assuming you have a working Python environment with
[Poetry](https://python-poetry.org/docs/#installation) installed you can get started
with:

```shell
git clone https://github.com/iscc/iscc-service-generator.git
cd iscc-service-generator
poetry install
poe install
```

# Demo production environment

To start a demo production environment:

1. Clone the repository:
2. Build docker images: `docker compose -f docker-compose.demo-prod.yml build`
3. Run Docker containers: `docker compose -f docker-compose.demo-prod.yml up -d`
4. Provision with development data: `docker compose -f docker-compose.demo-prod.yml exec backend python -m dev.install`
5. Access the environment via `http://localhost:8000/`

To inspect container logs:  `docker compose -f docker-compose.demo-prod.yml logs`

To stop the environment:   `docker compose -f docker-compose.demo-prod.yml stop`

To remove all data: `docker compose -f docker-compose.demo-prod.yml down -v`

You will need to change the `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` environment variables if the
environment is to be accessed externally by domain or IP and remove `127.0.0.1:` from the port
mapping of the backend container. All of those can be changed in the `docker-compose.demo-prod.yml`.
