# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/20"
from __future__ import absolute_import

import os
import sys
import restful_falcon

from runpy import run_path
from difflib import get_close_matches
from restful_falcon.util.file import list_files
from restful_falcon.core.constants import BANNER
from restful_falcon.core.management.base import CommandParser
from restful_falcon.core.management.base import CommandError
from restful_falcon.core.management.base import COMMANDS
from restful_falcon.apps.registry import apps


class ManagementUtility(object):
    """
    Encapsulate the logic of the restful-falcon-admin and manage.py utilities.
    """
    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])
        if ".py" in self.prog_name:
            self.prog_name = "python {}".format(self.prog_name)

    def main_help_text(self, commands_only=False):
        """Return the script's main help text, as a string."""
        if commands_only:
            usage = sorted(COMMANDS.keys())
        else:
            usage = [
                "",
                "Type '%s help <subcommand>' for help on a specific subcommand." % self.prog_name,
                "",
                "Available subcommands:",
            ]
            for name in sorted(COMMANDS.keys()):
                usage.append("    %s" % name)
        return "\n".join(usage)

    def fetch_command(self, subcommand):
        """
        Try to fetch the given subcommand, printing a message with the
        appropriate command called from the command line (usually
        "restful-falcon-admin" or "manage.py") if it can't be found.
        """
        # Get commands outside of try block to prevent swallowing exceptions
        try:
            command = COMMANDS[subcommand]()
        except KeyError:
            possible_matches = get_close_matches(subcommand, COMMANDS.keys())
            sys.stderr.write("Unknown command: %r" % subcommand)
            if possible_matches:
                sys.stderr.write(". Did you mean %s?" % possible_matches[0])
            sys.stderr.write("\nType '%s help' for usage.\n" % self.prog_name)
            sys.exit(1)
        return command

    # noinspection PyMethodMayBeStatic
    def load_commands(self):
        paths = [os.path.join(os.path.dirname(__file__), "commands")]
        for name in apps.app_configs:
            app_config = apps.app_configs[name]
            paths.append(os.path.join(
                os.path.dirname(app_config.module.__file__), "management/commands"
            ))
        for path in paths:
            for file in list_files(path, only_file=True):
                run_path(file)

    def execute(self):
        """
        Given the command-line arguments, figure out which subcommand is being
        run, create a parser appropriate to that command, and run it.
        """
        try:
            subcommand = self.argv[1]
        except IndexError:
            subcommand = "help"  # Display help if no arguments were given.

        # Preprocess options to extract --settings and --pythonpath.
        # These options could affect the commands that are available, so they
        # must be processed early.
        parser = CommandParser(usage="%(prog)s subcommand [options] [args]", add_help=False, allow_abbrev=False)
        parser.add_argument("--settings")
        parser.add_argument("--pythonpath")
        parser.add_argument("args", nargs="*")  # catch-all
        try:
            options, args = parser.parse_known_args(self.argv[2:])
        except CommandError:
            options, args = {}, ()  # Ignore any option errors at this point.

        sys.stdout.write(BANNER + "\n")
        if os.environ.get("RESTFUL_FALCON_CONFIG"):
            restful_falcon.setup()
        self.load_commands()

        if subcommand == "help":
            if "--commands" in args:
                sys.stdout.write(self.main_help_text(commands_only=True) + "\n")
            elif not options.args:
                sys.stdout.write(self.main_help_text() + '\n')
            else:
                self.fetch_command(options.args[0]).print_help(self.prog_name, options.args[0])
        # Special-cases: We want 'restful-falcon-admin --version' and
        # 'django-admin --help' to work, for backwards compatibility.
        elif subcommand == "version" or self.argv[1:] == ["--version"]:
            sys.stdout.write(restful_falcon.get_version() + "\n")
        elif self.argv[1:] in (["--help"], ["-h"]):
            sys.stdout.write(self.main_help_text() + "\n")
        else:
            self.fetch_command(subcommand).run_from_argv(self.argv)


def execute_from_command_line(argv=None):
    """Run a ManagementUtility."""
    utility = ManagementUtility(argv)
    utility.execute()
