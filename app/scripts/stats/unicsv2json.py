"""
Transform user info obtained from the University from multiple CSV files
into a single JSON document (for ease of futher use).

Usage:
    unicsv2json.py <camsiscodes.csv> <undergraduates.csv>

Options:
    <camsiscodes.csv>
        This is the camsis codes data available from:
        http://www.camsis.cam.ac.uk/cam-only/current_users/student-codes/

    <undergraduates.csv>
        A CSV version of the excel file provided by Education Section.
        The order of the columns is not important, as this program detects
        columns by name. The required columns are: "USN",
        "Academic Programme", "Academic Plan", "College",
        "Admit Term Description", "CRS Id Email Address"

        An example row might be:
        USN,Academic Programme,Academic Plan,College,Admit Term Description,CRS Id Email Address
        123456789,UGRD,LETX,HH,MT 2013,fb0@cam.ac.uk

Output:
    The output is written in JSON format to stdout.

        {
            [...]

            "abc123": {
                "college": "Hughes Hall",
                "start_year": 2013,
                "crsid": "abc123",
                "plans": [
                    {
                        "career": "Undergraduate",
                        "program": "Undergraduate",
                        "code": "LETX",
                        "name": "Land Economy Tripos"
                    }
                ]
            },

            [...]
        }
"""
import sys
import csv
import json
import itertools
import re

import docopt


# These are the columns we access from the CSV file.
COLUMNS = {
    "usn": "USN",
    "academic_programme": "Academic Programme",
    "academic_plan": "Academic Plan",
    "college": "College",
    "admit_term_desc": "Admit Term Description",
    "crsid_email": "CRS Id Email Address"
}


class ColumnMap(object):
    """
    Provides access to elements in a list of lists (e.g. CSV file) without
    hard coding the positions of columns.
    """
    def __init__(self, columns, mappings):
        self.column_map = dict((c, i) for i, c in enumerate(columns))

        self.generate_getters(mappings)

    def get_index(self, name):
        index = self.column_map.get(name)
        if index is None:
            raise KeyError("No such column: {!r}".format(name))
        return index

    def get_cell(self, row, name):
        return row[self.get_index(name)]

    def generate_getters(self, mappings):
        for method_name, col_name in mappings.items():
            # Need to create the getter funcs in their own func, otherwise
            # they share the same index var from the same closure.
            self.set_getter(method_name, col_name)

    def set_getter(self, method_name, column_name):
        index = self.get_index(column_name)
        getter = lambda row: row[index]
        setattr(self, "get_{}".format(method_name), getter)


def read_csv(file):
    return list(csv.reader(file))


def main(args):
    camsiscodes = read_csv(open(args["<camsiscodes.csv>"]))
    undergraduates = read_csv(open(args["<undergraduates.csv>"]))

    colmap = ColumnMap(undergraduates[0], COLUMNS)

    plans = extract_plans(camsiscodes,
                          extract_programs(camsiscodes),
                          extract_careers(camsiscodes))

    colleges = extract_colleges(camsiscodes)

    undergraduates_export = extract_undergrads(
        colmap, undergraduates[1:], plans, colleges)

    json.dump(undergraduates_export, sys.stdout, indent=4)


def extract_careers(camsiscodes):
    career_rows = (row for row in camsiscodes if row[0] == "D05")

    # Map career code -> name
    return dict((row[1], row[2]) for row in career_rows)


def extract_programs(camsiscodes):
    career_rows = (row for row in camsiscodes if row[0] == "D06")

    return dict(
        (
            row[1],
            {
                "description": row[2],
                "career_id": row[3]
            }
        )
        for row in career_rows
    )


def extract_colleges(camsiscodes):
    college_rows = (row for row in camsiscodes if row[0] == "A01")

    return dict((row[1], row[2]) for row in college_rows)


def extract_plans(camsiscodes, programs, careers):
    plan_rows = (row for row in camsiscodes if row[0] == "D08")

    plans = []
    for [_, plan_id, description, type_id, program_id, _] in plan_rows:
        plan = {
            "code": plan_id,
            "name": description
        }
        if program_id in programs:
            plan["program"] = programs[program_id]["description"]
            plan["career"] = careers[programs[program_id]["career_id"]]

        plans.append(plan)
    return dict((plan["code"], plan) for plan in plans)


def extract_undergrads(colmap, undergraduates, plans, colleges):
    key = colmap.get_usn
    undergraduates = sorted(undergraduates, key=key)
    groups = itertools.groupby(undergraduates, key)

    ugrads = {}
    for key, group in groups:
        rows = list(group)
        row = rows[0]

        crsid_match = re.match(r"(\w+)@cam\.ac\.uk", colmap.get_crsid_email(row))
        start_year_match = re.match(r"\w{2} (\d{4})",  colmap.get_admit_term_desc(row))

        college = colleges[colmap.get_college(row)]

        if not (crsid_match and start_year_match):
            print >> sys.stderr, "Ignoring malformed undergrad:", row
            continue

        ugrad = {
            "crsid": crsid_match.group(1),
            "start_year": int(start_year_match.group(1)),
            "college": college,
            "plans": [
                plans[colmap.get_academic_plan(row)] for row in rows
            ]
        }

        ugrads[ugrad["crsid"]] = ugrad
    return ugrads


if __name__ == "__main__":
    args = docopt.docopt(__doc__)
    main(args)