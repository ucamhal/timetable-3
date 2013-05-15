#!/bin/sh
export PATH=$PATH:/Library/PostgreSQL/9.0/bin
psql -U postgres << EOF

DROP DATABASE timetables2;
DROP ROLE timetables2;
DROP ROLE timetables2role;

EOF

