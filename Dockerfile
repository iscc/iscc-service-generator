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

# Install taglib
RUN apt-get update && \
  apt-get install --no-install-recommends -y libtag1-dev && \
  rm -rf /var/lib/apt/lists

# Install Poetry and create venv
# hadolint ignore=DL3013
RUN pip install -U pip wheel setuptools && \
  pip install "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

#
# dev-runtime
#

FROM builder AS dev-runtime

RUN apt-get update && apt-get install -y --no-install-recommends inotify-tools pslist && rm -rf /var/lib/apt/lists

RUN poetry install

# hadolint ignore=DL3059
RUN poetry run python -c "import iscc_sdk; iscc_sdk.tools.install()"

COPY docker/entrypoint-dev.sh /app/docker/
COPY docker/qcluster-autoreload.sh /app/docker/
ENTRYPOINT [ "docker/entrypoint-dev.sh" ]

EXPOSE 8000/tcp

CMD ["poetry", "run", "uvicorn", "iscc_service_generator.asgi:application", "--host=0.0.0.0", "--reload"]

#
# prod-build
#

FROM builder AS prod-build

# hadolint ignore=SC1091
RUN python -m venv /venv && . /venv/bin/activate && poetry install --no-dev --no-root

RUN /venv/bin/python -c "import iscc_sdk; iscc_sdk.tools.install()"

COPY . /app/

# hadolint ignore=DL3059
RUN DJANGO_SECRET_KEY=foobar /venv/bin/python manage.py collectstatic --no-input

#
# prod-runtime
#

FROM python:3.9-slim AS prod-runtime

LABEL org.opencontainers.image.source=https://github.com/iscc/iscc-service-generator

RUN apt-get update && apt-get install --no-install-recommends -y libmagic1 libpq5 libtag1v5-vanilla && rm -rf /var/lib/apt/lists

# Disable stdout/stderr buggering, can cause issues with Docker logs
ENV PYTHONUNBUFFERED=1

ENV PATH="/venv/bin:$PATH"
ENV VIRTUAL_ENV=/venv

COPY docker/worker.sh /usr/local/bin/worker

COPY --from=prod-build /root/.local/share/iscc-sdk /root/.local/share/iscc-sdk
COPY --from=prod-build /root/.ipfs /root/.ipfs
COPY --from=prod-build /app /app
COPY --from=prod-build /venv /venv

WORKDIR /app

ENTRYPOINT [ "docker/entrypoint-prod.sh" ]

EXPOSE 8000/tcp

CMD ["uvicorn", "iscc_service_generator.asgi:application", "--host=0.0.0.0"]
