"""

Usage:
    stats2html.py <stats.json> <template_dir> <outdir>

"""
from __future__ import unicode_literals

import json
from os.path import join
from urllib import quote_plus
import hashlib

import docopt
import jinja2


class Stats2Html(object):
    def __init__(self, args):
        self.args = args

    def get_stats_path(self):
        return self.args["<stats.json>"]

    def get_stats(self):
        with open(self.get_stats_path()) as f:
            return json.load(f)

    def get_template_dir(self):
        return self.args["<template_dir>"]

    def get_template_loader(self):
        return jinja2.FileSystemLoader(self.get_template_dir())

    def get_template_environment(self):
        loader = self.get_template_loader()

        env = jinja2.Environment(loader=loader, autoescape=True)
        env.filters["dataset_filename"] = get_dataset_filename

        return env

    def enumerate_stats(self, stats):
        yield stats
        #return # DEBUG

        for drilldown, substats_list in stats.get("drilldowns", {}).iteritems():
            for substats in substats_list:
                for stats in self.enumerate_stats(substats):
                    yield stats

    def get_out_dir(self):
        return args["<outdir>"]

    def main(self):
        env = self.get_template_environment()
        stats_tree = self.get_stats()

        all_stats = list(self.enumerate_stats(stats_tree))
        stats_count = len(all_stats)
        print "Stats count:", stats_count

        for stats in all_stats:
            self.render(stats, env)

    def render(self, stats, env):
        name = stats["name"]
        try:
            template = env.get_template("stats-{}.html".format(name))
        except jinja2.TemplateNotFound:
            template = env.get_template("stats.html")

        context = self.get_stats_context(stats)
        html = template.render(context)

        filename = get_dataset_filename(stats["dataset"])
        path = join(self.get_out_dir(), filename)

        with open(path, "w") as f:
            f.write(html)

    def get_stats_context(self, stats):
        return {
            "stats": stats,
            "datasets": get_flat_datasets(stats["dataset"])
        }

def get_flat_datasets(dataset):
    if dataset.get("parent") is None:
        return [dataset]
    return get_flat_datasets(dataset["parent"]) + [dataset]


def get_dataset_filename(dataset):
    dataset_name = get_dataset_filename_representation(dataset)

    # We easilly hit filename length limits, so we'll have to hash around that
    # issue. :/
    if dataset_name != "root":
        dataset_name = hashlib.md5(dataset_name).hexdigest()

    return "{}.html".format(dataset_name)


def get_dataset_filename_representation(dataset):
    parent = dataset.get("parent")

    assert dataset["operations"] or parent is None, dataset

    if parent is not None:
        path = ",".join(
            get_operation_filename_representation(op)
            for op in dataset["operations"]
        )
        return get_dataset_filename_representation(parent) + ";" + path
    return "root"

def get_operation_filename_representation(operation):
    if operation["type"] == "filter":
        return "{}={}".format(
            quote_plus(operation["name"]),
            quote_plus("{}".format(operation["filter_value"]))
        )
    elif operation["type"] == "pivot":
        return "pivot-{}".format(quote_plus(operation["name"]))

    raise ValueError("Unknown operation type", operation["type"])


if __name__ == "__main__":
    args = docopt.docopt(__doc__)

    Stats2Html(args).main()