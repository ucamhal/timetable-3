#!/bin/sh
export PATH=$PATH:/Library/PostgreSQL/9.0/bin
psql -U postgres << EOF

CREATE ROLE timetables2role
  NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE;

CREATE ROLE timetables2 LOGIN
  PASSWORD 'timetables2'
  NOSUPERUSER INHERIT CREATEDB NOCREATEROLE;
GRANT timetables2role TO timetables2;

CREATE DATABASE timetables2
  WITH OWNER = timetables2
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'en_GB.UTF-8'
       LC_CTYPE = 'en_GB.UTF-8'
       CONNECTION LIMIT = -1;

EOF

