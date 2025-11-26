FROM python:3.12.11 AS backend

WORKDIR "/app"
# install
COPY ./requirements.txt ./
RUN ["python3", "-m", "pip", "install", "--no-deps", "--no-cache-dir", "-r", "requirements.txt"]
# run
COPY ./apps/backend/ ./backend/
ENTRYPOINT ["python3", "-m", "uvicorn", "backend.main:app"]


FROM python:3.12.11 AS auth

WORKDIR "/app"
# install
COPY ./requirements.txt ./
RUN ["python3", "-m", "pip", "install", "--no-deps", "--no-cache-dir", "-r", "requirements.txt"]
# run
COPY ./apps/auth/ ./auth/
ENTRYPOINT ["python3", "-m", "uvicorn", "auth.main:app"]


FROM node:alpine AS frontadmin

ENV VITE_PUBLIC_URL=/admin
WORKDIR "/app"
# install
COPY ./apps/front-admin/package.json ./
COPY ./apps/front-admin/package-lock.json ./
RUN ["npm", "ci"]
# build
COPY ./apps/front-admin/ .
RUN ["npm", "run", "build"]


FROM nginx:alpine AS reverseproxy

# config
COPY ./config/nginx/conf/mime.types /etc/nginx/conf.d/mime.types
COPY ./config/nginx/conf/nginx-prod.conf.template /etc/nginx/templates/default.conf.template
# frontend
COPY ./apps/frontend/ /www/frontend/
# admin frontend
COPY --from=frontadmin /app/dist/ /www/admin/
