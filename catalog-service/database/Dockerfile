FROM mysql:latest

WORKDIR /app

COPY ./scripts/db/init.sh /docker-entrypoint-initdb.d/init.sh
COPY ./scripts/db/dump.sql ./scripts/db/dump.sql

RUN chmod +x /docker-entrypoint-initdb.d/init.sh
RUN . /docker-entrypoint-initdb.d/init.sh