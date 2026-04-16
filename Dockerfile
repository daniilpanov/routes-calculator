FROM python:3.12-slim AS python-apps

ARG USERNAME="appuser"
ARG USER_UID=1000
ARG USER_GID=1000
ARG APP_DIR="/apps"

RUN mkdir -p /home/${USERNAME} && \
    groupadd -r -g ${USER_GID} ${USERNAME} && \
    useradd -r -d /home/${USERNAME} -u ${USER_UID} -g ${USER_GID} ${USERNAME} && \
    chown ${USERNAME}:${USERNAME} /home/${USERNAME} && \
    mkdir ${APP_DIR} && \
    chmod 750 ${APP_DIR} && \
    chown ${USERNAME}:${USERNAME} ${APP_DIR}

USER ${USER_UID}

# install requirements
COPY ./requirements.txt ./
RUN ["python3", "-m", "pip", "install", "--no-deps", "--no-cache-dir", "-r", "requirements.txt"]

WORKDIR "${APP_DIR}"
# run
COPY ./apps/ ./
ENTRYPOINT ["python3", "-m", "uvicorn"]

FROM python:3.12-slim AS db-migration

ARG USERNAME="appuser"
ARG USER_UID=1000
ARG USER_GID=1000
ARG APP_DIR="/app"

RUN mkdir -p /home/${USERNAME} && \
    groupadd -r -g ${USER_GID} ${USERNAME} && \
    useradd -r -d /home/${USERNAME} -u ${USER_UID} -g ${USER_GID} ${USERNAME} && \
    chown ${USERNAME}:${USERNAME} /home/${USERNAME} && \
    mkdir ${APP_DIR} && \
    chmod 750 ${APP_DIR} && \
    chown ${USERNAME}:${USERNAME} ${APP_DIR}

USER ${USER_UID}

# install requirements
COPY ./requirements.txt ./
RUN ["python3", "-m", "pip", "install", "--no-deps", "--no-cache-dir", "-r", "requirements.txt"]

WORKDIR "${APP_DIR}"
# run
COPY ./alembic.ini ./alembic.ini
COPY ./alembic/ ./alembic/
COPY ./apps/ ./apps/

ENTRYPOINT ["python3", "-m", "alembic"]

FROM node:alpine AS frontend

USER "node"

WORKDIR "/app"
# install
COPY ./Node/apps/new-frontend/package.json ./package.json
COPY ./Node/apps/new-frontend/package-lock.json ./package-lock.json
RUN ["npm", "ci"]
# run
COPY ./Node/apps/new-frontend/ ./
ENTRYPOINT ["npm"]


FROM frontend AS frontend-builder
RUN ["npm", "run", "build"]


FROM node:alpine AS frontadmin

USER "node"

WORKDIR "/app"
# install
COPY ./Node/apps/front-admin/package.json ./package.json
COPY ./Node/apps/front-admin/package-lock.json ./package-lock.json
RUN ["npm", "ci"]
# run
COPY ./Node/apps/front-admin/ ./
ENTRYPOINT ["npm"]


FROM frontadmin AS frontadmin-builder

ENV VITE_PUBLIC_URL=/admin
RUN ["npm", "run", "build"]


FROM nginx:alpine AS reverseproxy

# config
COPY ./config/nginx/conf/mime.types /etc/nginx/conf.d/mime.types
COPY config/nginx/conf/nginx.conf.template /etc/nginx/templates/default.conf.template
# old frontend
COPY ./Node/apps/frontend/ /www/old-frontend/
# frontend
COPY --from=frontend-builder /app/dist/ /www/frontend/
# admin frontend
COPY --from=frontadmin-builder /app/dist/ /www/admin/
