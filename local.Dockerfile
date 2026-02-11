FROM python:3.12-slim AS calculator

# install
COPY ./requirements.txt ./
RUN ["python3", "-m", "pip", "install", "--no-deps", "--no-cache-dir", "-r", "requirements.txt"]
# run
WORKDIR "/app"
ENTRYPOINT ["python3", "-m", "uvicorn"]


FROM node:alpine AS frontadmin

WORKDIR "/app"
# install
COPY ./apps/front-admin/package.json ./package.json
COPY ./apps/front-admin/package-lock.json ./package-lock.json
RUN ["npm", "ci"]
# run
ENTRYPOINT ["npm"]


FROM mariadb:latest AS database

FROM phpmyadmin:latest AS dbadmin

FROM nginx:alpine AS reverseproxy
