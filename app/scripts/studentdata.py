#!/usr/bin/env python
"""
Utility to assist with joining CRSID data from education section with data from
the camsis coding manual to create a mapping of CRSID -> Tripos (roughly). I
say roughly because we map to "Academic Plans" which are not necessarily a 1:1
map to tripos...

To use this you'll need to run each of the 4 subcommands listed under usage.
First to init a db with required tables, then 2 commands to load data, then the
export to spit out JSON. Alternatively you'll have the data in the db so you
can query it however you like instead of using export.

Usage:
    studentdata.py init <db_path>
    studentdata.py load crsids <db_path> <crsids_csv_path>
    studentdata.py load camsis-codes <db_path> <camsis_codes_csv_path>
    studentdata.py generate aliases <db_path> --seed=<seed> [--len=<n>]
    studentdata.py export json <db_path>
    studentdata.py export csv <db_path>

Arguments:
    db_path: Path to an sqlite 3 database to operate on.
    crsids_csv_path: A CSV file with columns: USN,Name,Academic Programme,
                     Academic Plan,Admit Term,CRS Id Email Address

                     The email addresses should be crsid@cam.ac.uk
    camsis_codes_csv_path: The CSV export from http://www.camsis.cam.ac.uk/cam-only/current_users/student-codes/
    --len: The length (in characters) of the generated alias.
"""
from __future__ import unicode_literals

import csv
import hashlib
import json
import re
import sqlite3
import sys

import base32_crockford
import docopt


class Command(object):
    create_table_sql = """
    CREATE TABLE student (usn UNIQUE, name, academic_programme, academic_plan, admin_term, email, crsid UNIQUE);

    CREATE TABLE academic_plan (id UNIQUE, description, type, academic_programme, process_date);

    CREATE TABLE plan_alias (academic_plan_id UNIQUE, alias UNIQUE, seed);
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

    def get_export_cursor(self):
        conn = self.get_db_connection()
        return conn.execute("SELECT crsid, academic_plan.description, academic_plan.id, plan_alias.alias "
                              "FROM student "
                              "JOIN academic_plan ON student.academic_plan = academic_plan.id "
                              "JOIN plan_alias ON student.academic_plan = plan_alias.academic_plan_id "
                              "WHERE student.crsid IS NOT NULL")

    def export_json(self):
        cursor = self.get_export_cursor()

        export_data = dict(
            (crsid, {"academic_plan": description, "academic_plan_id": plan_id, "plan_alias": alias})
            for (crsid, description, plan_id, alias) in cursor
        )
        json.dump(export_data, sys.stdout, indent=4)

    def export_csv(self):
        cursor = self.get_export_cursor()

        rows = [["CRSID", "Academic Plan", "Academic Plan ID", "Plan Alias"]]
        rows += map(list, cursor)

        csv.writer(sys.stdout).writerows(rows)

    def get_alias_seed(self):
        seed = self.args["--seed"]
        if not seed:
            raise ValueError("A --seed value is required.")
        return seed

    def get_alias_len(self):
        raw = self.args["--len"]
        if raw is None:
            return 6

        alias_len = int(raw)
        if alias_len < 1:
            raise ValueError("--len must be > 0")
        return alias_len

    def generate_alias(self, plan):
        md5 = hashlib.md5()
        md5.update(self.get_alias_seed())
        md5.update(plan[b"id"])
        md5.update(plan[b"description"])
        num = int(md5.hexdigest(), 16)
        return base32_crockford.encode(num)[:self.get_alias_len()]

    def detect_duplicates(self, aliases):
        dupes = set()
        count = 0
        unique = set()
        for _, alias, _ in aliases:
            unique.add(alias)
            if len(unique) == count:
                dupes.add(alias)
            count = len(unique)

        if dupes:
            raise ValueError("Duplicate aliases found", dupes)

    def generate_aliases(self):
        conn = self.get_db_connection()
        plans = conn.execute("SELECT * FROM academic_plan")
        aliases = [
            (plan[b"id"], self.generate_alias(plan), self.get_alias_seed())
            for plan in plans
        ]

        self.detect_duplicates(aliases)

        conn.executemany("INSERT INTO plan_alias VALUES (?,?,?)", aliases)
        conn.commit()


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


def generate_aliases(args):
    Command(args).generate_aliases()


def export_json(args):
    Command(args).export_json()


def export_csv(args):
    Command(args).export_csv()


if __name__ == "__main__":
    args = docopt.docopt(__doc__)

    if args["init"]:
        init(args)
    elif args["load"] and args["crsids"]:
        load_crsids(args)
    elif args["load"] and args["camsis-codes"]:
        load_camsis_codes(args)
    elif args["generate"] and args ["aliases"]:
        generate_aliases(args)
    elif args["export"] and args["json"]:
        export_json(args)
    elif args["export"] and args["csv"]:
        export_csv(args)
    else:
        assert False, ("Not all argument cases handled.", args)
