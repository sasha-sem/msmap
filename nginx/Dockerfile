FROM nginx:1.19.0-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY frontend /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d