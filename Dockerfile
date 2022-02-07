FROM python:3.9 AS builder

ARG POETRY_VERSION=1.1.12

# Disable stdout/stderr buggering, can cause issues with Docker logs
ENV PYTHONUNBUFFERED=1

# Disable some obvious pip functionality
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_NO_CACHE_DIR=1

# Configure poetry
ENV POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_PATH=/venvs


# Install Poetry and create venv
RUN pip install -U pip wheel setuptools && \
  pip install "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

FROM builder AS dev-runtime

RUN poetry install && \
  poetry run python -c "import iscc; iscc.bin.install()"

COPY docker/entrypoint-dev.sh /app/docker/
ENTRYPOINT [ "docker/entrypoint-dev.sh" ]

EXPOSE 8000/tcp

CMD ["poetry", "run", "uvicorn", "iscc_service_generator.asgi:application", "--host=0.0.0.0", "--reload"]
