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

#
# dev-runtime
#

FROM builder AS dev-runtime

RUN poetry install

RUN poetry run python -c "import iscc_sdk; iscc_sdk.tools.install()"

COPY docker/entrypoint-dev.sh /app/docker/
ENTRYPOINT [ "docker/entrypoint-dev.sh" ]

#
# dev-runtime-backend
#

FROM dev-runtime AS dev-runtime-backend

EXPOSE 8000/tcp

CMD ["poetry", "run", "uvicorn", "iscc_service_generator.asgi:application", "--host=0.0.0.0", "--reload"]

#
# dev-runtime-worker
#

FROM dev-runtime AS dev-runtime-worker

RUN apt-get update && apt-get install -y inotify-tools pslist && rm -rf /var/lib/apt/lists

COPY docker/qcluster-autoreload.sh /app/docker/

CMD ["docker/qcluster-autoreload.sh"]

#
# prod-build
#

FROM builder AS prod-build

RUN python -m venv /venv && . /venv/bin/activate && poetry install --no-dev --no-root

RUN /venv/bin/python -c "import iscc; iscc.bin.install()"

COPY . /app/

#
# prod-runtime
#

FROM python:3.9-slim AS prod-runtime

RUN apt-get update && apt-get install --no-install-recommends -y libmagic1 libpq5 && rm -rf /var/lib/apt/lists

# Disable stdout/stderr buggering, can cause issues with Docker logs
ENV PYTHONUNBUFFERED=1

ENV PATH="/venv/bin:$PATH"
ENV VIRTUAL_ENV=/venv

COPY --from=prod-build /root/.config/iscc /root/.config/iscc
COPY --from=prod-build /app /app
COPY --from=prod-build /venv /venv

WORKDIR /app

ENTRYPOINT [ "docker/entrypoint-prod.sh" ]

#
# prod-runtime-backend
#

FROM prod-runtime AS prod-runtime-backend

EXPOSE 8000/tcp

CMD ["uvicorn", "iscc_service_generator.asgi:application", "--host=0.0.0.0"]

#
# prod-runtime-worker
#

FROM prod-runtime AS prod-runtime-worker

CMD ["python", "manage.py", "qcluster"]
