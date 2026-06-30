FROM python:3.12-slim AS python-base

ARG USERNAME="appuser"
ARG USER_UID=1000
ARG USER_GID=1000
ARG APP_DIR="/workspace"

RUN mkdir -p /home/${USERNAME} && \
    groupadd -r -g ${USER_GID} ${USERNAME} && \
    useradd -r -d /home/${USERNAME} -u ${USER_UID} -g ${USER_GID} ${USERNAME} && \
    chown ${USERNAME}:${USERNAME} /home/${USERNAME} && \
    mkdir ${APP_DIR} && \
    chmod 750 ${APP_DIR} && \
    chown ${USERNAME}:${USERNAME} ${APP_DIR}

RUN mkdir /var/log/app
RUN chown ${USERNAME}:${USERNAME} /var/log/app

USER ${USER_UID}

COPY ./requirements.txt ./
RUN ["python3", "-m", "pip", "install", "--no-deps", "--no-cache-dir", "-r", "requirements.txt"]

WORKDIR "${APP_DIR}"


FROM python-base AS python-apps

COPY ./apps/ ./
ENTRYPOINT ["python3", "-m", "uvicorn"]


FROM python-base AS db-migration

COPY ./alembic.ini ./alembic.ini
COPY ./alembic/ ./alembic/
COPY ./apps/ ./apps/

ENTRYPOINT ["python3", "-m", "alembic"]


FROM python-base AS test-runner

COPY ./requirements-tests.txt ./
RUN ["python3", "-m", "pip", "install", "--no-deps", "--no-cache-dir", "-r", "requirements-tests.txt"]

COPY ./apps/ ./apps/
COPY ./tests/ ./tests/

ENTRYPOINT ["python3", "-m", "pytest"]
# ENV does not work properly in JSON mode
CMD ["/workspace/tests", "-v", "--tb=short", "--override-ini=pythonpath=/workspace/apps", "--override-ini=asyncio_mode=auto", "--rootdir=/workspace"]
