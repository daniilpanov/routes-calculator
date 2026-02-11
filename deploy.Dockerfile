FROM python:3.12-slim AS python-apps

# install requirements
COPY ./requirements.txt ./
RUN ["python3", "-m", "pip", "install", "--no-deps", "--no-cache-dir", "-r", "requirements.txt"]

WORKDIR "/apps"
# run
COPY ./apps/ ./
ENTRYPOINT ["python3", "-m", "uvicorn"]


FROM node:alpine AS frontadmin

ENV VITE_PUBLIC_URL=/admin
WORKDIR "/app"
# install dependencies
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
