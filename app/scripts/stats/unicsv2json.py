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
        The columns are:
        USN,Name,Academic Plan,Admit Term Description,Expected Graduation Term Descr,CRS Id Email Address

        An example row might be:
        123456789,"Bar,Foo",MATX,MT 2012,ET 2015,fb0@cam.ac.uk

Output:
    The output is written in JSON format to stdout.

        {
            [...]

            "fb0": {
                "plans": [
                    {"code": "MATX", "name": "Mathematical Tripos"}
                ],
                "start_year": "2012",
                "end_year": 2015,
                "name": "Bar,Foo"
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


def read_csv(file):
    return list(csv.reader(file))


def main(args):
    camsiscodes = read_csv(open(args["<camsiscodes.csv>"]))
    undergraduates = read_csv(open(args["<undergraduates.csv>"]))

    plans = extract_plans(camsiscodes,
                          extract_programs(camsiscodes),
                          extract_careers(camsiscodes))

    undergraduates_export = extract_undergrads(undergraduates, plans)

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


def extract_undergrads(undergraduates, plans):
    key = lambda row: row[0]
    undergraduates = sorted(undergraduates, key=key)
    groups = itertools.groupby(undergraduates, key)

    ugrads = {}
    for key, group in groups:
        rows = list(group)
        row = rows[0]

        crsid_match = re.match(r"(\w+)@cam\.ac\.uk", row[5])
        start_year_match = re.match(r"\w{2} (\d{4})",  row[3])
        end_year_match = re.match(r"\w{2} (\d{4})",  row[4])

        if not (crsid_match and start_year_match and end_year_match):
            print >> sys.stderr, "Ignoring malformed undergrad:", row
            continue

        ugrad = {
            "name": row[1],
            "crsid": crsid_match.group(1),
            "start_year": int(start_year_match.group(1)),
            "end_year": int(end_year_match.group(1)),
            "plans": [
                plans[row[2]] for row in rows
            ]
        }

        ugrads[ugrad["crsid"]] = ugrad
    return ugrads


if __name__ == "__main__":
    args = docopt.docopt(__doc__)
    main(args)