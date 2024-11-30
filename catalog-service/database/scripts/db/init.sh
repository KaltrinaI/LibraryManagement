#!/bin/bash
set -e

mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" < ./dump.sql

