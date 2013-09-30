#!/usr/bin/env python
"""
Utility to assist with joining CRSID data from education section with data from
the camsis coding manual to create a mapping of CRSID -> Tripos (roughly). I say
roughly because we map to "Academic Plans" which are not neccisarilly a 1:1 map
to tripos...

To use this you'll need to run each of the 4 subcommands listed under usage.
First to init a db with required tables, then 2 commands to load data, then the
export to spit out JSON. Alternatively you'll have the data in the db so you
can query it however you like instead of using export.

Usage:
    studentdata.py init <db_path>
    studentdata.py load crsids <db_path> <crsids_csv_path>
    studentdata.py load camsis-codes <db_path> <camsis_codes_csv_path>
    studentdata.py export json <db_path>

Arguments:
    db_path: Path to an sqlite 3 database to operate on.
    crsids_csv_path: A CSV file with columns: USN,Name,Academic Programme,
                     Academic Plan,Admit Term,CRS Id Email Address

                     The email addresses should be crsid@cam.ac.uk
    camsis_codes_csv_path: The CSV export from http://www.camsis.cam.ac.uk/cam-only/current_users/student-codes/
"""
from __future__ import unicode_literals

import sys
import sqlite3
import csv
import re
import json

import docopt


class Command(object):
    create_table_sql = """
    CREATE TABLE student (usn, name, academic_programme, academic_plan, admin_term, email, crsid);
    CREATE UNIQUE INDEX student_crsid on student (crsid);
    CREATE UNIQUE INDEX student_usn on student (usn);

    CREATE TABLE academic_plan (id, description, type, academic_programme, process_date);
    CREATE UNIQUE INDEX academic_plan_id on academic_plan (id);
    """

    def __init__(self, args):
        self.args = args

    def get_db_path(self):
        return self.args["<db_path>"]

    def get_db_connection(self):
        conn = sqlite3.connect(self.get_db_path())
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_db_connection()
        conn.executescript(self.create_table_sql)
        return conn

    def get_crsids_path(self):
        return self.args["<crsids_csv_path>"]

    def get_crsids_stream(self):
        return open_path(self.get_crsids_path())

    def extract_crsid(self, email):
        match = re.match(r"^(.*)@cam\.ac\.uk$", email)
        if not match:
            return None
        return match.group(1)

    def extract_crsids(self, data):
        return [
            row + [self.extract_crsid(row[5])]
            for row in data
        ]

    def load_crsids(self):
        data = load_csv(self.get_crsids_stream())
        data_with_crsids = self.extract_crsids(data)
        
        conn = self.get_db_connection()
        conn.executemany("INSERT INTO student VALUES (?,?,?,?,?,?,?)",
                         data_with_crsids)
        conn.commit()

    def get_camsis_codes_path(self):
        return self.args["<camsis_codes_csv_path>"]

    def get_camsis_codes_stream(self):
        return open_path(self.get_camsis_codes_path())

    def load_camsis_codes(self):
        data = load_csv(self.get_camsis_codes_stream())
        academic_plans = filter_camsis_csv_to_section("D08", data)

        conn = self.get_db_connection()
        conn.executemany("INSERT INTO academic_plan VALUES (?,?,?,?,?)",
                         academic_plans)
        conn.commit()

    def export_json(self):
        conn = self.get_db_connection()
        cursor = conn.execute("SELECT crsid, academic_plan.description, academic_plan.id "
                              "FROM student JOIN academic_plan "
                              "ON student.academic_plan = academic_plan.id "
                              "WHERE student.crsid IS NOT NULL")

        export_data = dict(
            (crsid, {"academic_plan": description, "academic_plan_id": plan_id})
            for (crsid, description, plan_id) in cursor
        )
        json.dump(export_data, sys.stdout, indent=4)


def filter_camsis_csv_to_section(section, data):
    return [
        row[1:] for row in data
        if row[0] == section
    ]

def open_path(path):
    if path == "-":
        return sys.stdin
    return open(path)

def load_csv(file, strip_head=True, encoding="utf-8"):
    rows = list(csv.reader(file))
    if strip_head is True:
        rows = rows[1:]

    # Decode all data into strings (this assumes all cells are strings)
    return [[s.decode(encoding) for s in row] for row in rows]


def init(args):
    Command(args).init_db()


def load_crsids(args):
    Command(args).load_crsids()


def load_camsis_codes(args):
    Command(args).load_camsis_codes()


def export_json(args):
    Command(args).export_json()


if __name__ == "__main__":
    args = docopt.docopt(__doc__)

    if args["init"]:
        init(args)
    elif args["load"] and args["crsids"]:
        load_crsids(args)
    elif args["load"] and args["camsis-codes"]:
        load_camsis_codes(args)
    elif args["export"]:
        export_json(args)
    else:
        assert False, ("Not all argument cases handled.", args)
