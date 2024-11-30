FROM mysql:latest

WORKDIR /app

COPY ./scripts/db/init.sh /docker-entrypoint-initdb.d/init.sh
COPY ./scripts/db/dump.sql /docker-entrypoint-initdb.d/dump.sql

RUN chmod +x /docker-entrypoint-initdb.d/init.sh