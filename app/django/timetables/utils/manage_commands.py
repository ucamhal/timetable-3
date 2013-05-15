from django.core.management.base import BaseCommand

class ArgparseBaseCommand(BaseCommand):
    """
    A manage.py Command class which uses argparse to parse args instead of
    optparse.

    To use, ensure self.parser is an argparse parser instance, then implement
    handle(self, args) as normal. The args argument in handle() will be the
    parsed arguments.
    """

    # Override run_from_argv to use argparse to parse arguments instead of
    # optparse.
    def run_from_argv(self, argv):
        args = self.parser.parse_args(argv[2:])
        # execute() ends up calling handle with args...
        self.execute(args)
