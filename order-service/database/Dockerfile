FROM mysql:latest

WORKDIR /app

# Copy initialization scripts
COPY ./scripts/db/dump.sql /docker-entrypoint-initdb.d/dump.sql
