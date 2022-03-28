FROM debian:bullseye-slim

RUN apt-get update && apt-get -y upgrade

RUN apt-get install -y nginx

COPY ./url-shorter.conf /etc/nginx/conf.d/url-shorter.conf

ENTRYPOINT ["nginx", "-g", "daemon off;"]