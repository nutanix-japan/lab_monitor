#!/bin/sh
sed -e "s/{{PORT}}/$PORT/g" /etc/nginx/nginx.tpl > /etc/nginx/nginx.conf
sed -i -e "s/{{API_TEMPERATURE_HOST}}/$API_TEMPERATURE_HOST/g" /etc/nginx/nginx.conf
sed -i -e "s/{{API_TEMPERATURE_PORT}}/$API_TEMPERATURE_PORT/g" /etc/nginx/nginx.conf
exec nginx -g "daemon off;"