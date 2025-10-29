FROM python:3.12.11 AS calculator

COPY ./requirements.txt ./
RUN ["python3", "-m", "pip", "install", "--no-deps", "--no-cache-dir", "-r", "requirements.txt"]

WORKDIR "/app"
ENTRYPOINT ["python3", "-m", "uvicorn"]


FROM node:alpine AS front

WORKDIR "/app"
ENTRYPOINT ["npm"]


FROM mariadb:latest AS database

FROM phpmyadmin:latest AS dbadmin

FROM nginx:alpine AS reverseproxy
