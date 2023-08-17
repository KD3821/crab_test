FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
COPY proxy_params /etc/nginx

COPY /etc/letsencrypt/live/mysoft78.ru/fullchain.pem /etc/letsencrypt/live/mysoft78.ru/
COPY /etc/letsencrypt/live/mysoft78.ru/privkey.pem /etc/letsencrypt/live/mysoft78.ru/
COPY /etc/letsencrypt/options-ssl-nginx.conf /etc/letsencrypt/
COPY /etc/letsencrypt/options-ssl-nginx.conf /etc/letsencrypt/
COPY /etc/letsencrypt/ssl-dhparams.pem /etc/letsencrypt/
