FROM node:alpine AS frontend

USER "node"

WORKDIR "/app"
# install
COPY ./apps/user-frontend/package.json ./package.json
COPY ./apps/user-frontend/package-lock.json ./package-lock.json
RUN ["npm", "ci"]
# run
COPY ./apps/user-frontend/ ./
ENTRYPOINT ["npm"]


FROM frontend AS frontend-builder
RUN ["npm", "run", "build"]


FROM node:alpine AS frontadmin

USER "node"

WORKDIR "/app"
# install
COPY ./apps/admin-frontend/package.json ./package.json
COPY ./apps/admin-frontend/package-lock.json ./package-lock.json
RUN ["npm", "ci"]
# run
COPY ./apps/admin-frontend/ ./
ENTRYPOINT ["npm"]


FROM frontadmin AS frontadmin-builder

ENV VITE_PUBLIC_URL=/admin
RUN ["npm", "run", "build"]
