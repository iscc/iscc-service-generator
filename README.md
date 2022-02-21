# ISCC Generator - Web Service

**A microservice with REST API and management dashboard for generating ISCC codes**

## Development Status

Under development ...

# Development Quickstart

## With docker

```shell
git clone https://github.com/iscc/iscc-service-generator.git
cd iscc-service-generator
docker compose build
docker compose up
```

- Access interactive Rest API docs via http://localhost:8000/api/docs
- Access operator dashboard at http://localhost:8000 with user `demo` password `demo`


## With local Python environment
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
3. Run Docker containers: `docker compose -f docker-compose.demo-prod.yml up`
4. Wait for backend container to start (`Application startup complete` in log)
5. Access interactive Rest API docs via http://localhost:8000/api/docs

Optional: To get access to the operator dashboard

6. In a separate shell run: `docker compose -f docker-compose.demo-prod.yml exec backend python -m dev.install`
7. See user account information in output
8. Access operator dashboard via `http://localhost:8000/`

To remove all data: `docker compose -f docker-compose.demo-prod.yml down -v`

You will need to change the `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` environment variables if the
environment is to be accessed externally by domain or IP and remove `127.0.0.1:` from the port
mapping of the backend container. All of those can be changed in the `docker-compose.demo-prod.yml`.
