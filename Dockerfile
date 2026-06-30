FROM nginx:alpine AS reverseproxy

ARG FRONTEND_APP_USER_WORKDIR="/workspace"
ARG FRONTEND_APP_ADMIN_WORKDIR="/workspace"

# config
COPY ./config/nginx/conf/mime.types /etc/nginx/conf.d/mime.types
COPY config/nginx/conf/nginx.conf.template /etc/nginx/templates/default.conf.template
# frontend
COPY --from=frontend-builder ${FRONTEND_APP_USER_WORKDIR}/dist/ /www/frontend/
# admin frontend
COPY --from=frontadmin-builder ${FRONTEND_APP_ADMIN_WORKDIR}/dist/ /www/admin/
