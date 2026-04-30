FROM nginx:alpine AS reverseproxy

# config
COPY ./config/nginx/conf/mime.types /etc/nginx/conf.d/mime.types
COPY config/nginx/conf/nginx.conf.template /etc/nginx/templates/default.conf.template
# frontend
COPY --from=frontend-builder /app/dist/ /www/frontend/
# admin frontend
COPY --from=frontadmin-builder /app/dist/ /www/admin/
