FROM python:3.12 AS calculator

COPY ./requirements.txt ./
RUN ["python3", "-m", "pip", "install", "-r", "requirements.txt"]

WORKDIR '/app'

ENTRYPOINT ["python3", "-m", "fastapi", "run"]

FROM mariadb:latest AS database

FROM adminer:latest AS dbadmin
