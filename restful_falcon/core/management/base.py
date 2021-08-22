# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/1"
from __future__ import absolute_import

import sys
from argparse import ArgumentParser
from argparse import HelpFormatter

import os
from io import TextIOBase

import restful_falcon

__all__ = ["CommandError", "BaseCommand"]

COMMANDS = {}


class CommandError(Exception):
    """
    Exception class indicating a problem while executing a management
    command.

    If this exception is raised during the execution of a management
    command, it will be caught and turned into a nicely-printed error
    message to the appropriate output stream (i.e., stderr); as a
    result, raising this exception (with a sensible description of the
    error) is the preferred way to indicate that something has gone
    wrong in the execution of a command.
    """
    pass


class SystemCheckError(CommandError):
    """
    The system check framework detected unrecoverable errors.
    """
    pass


class CommandParser(ArgumentParser):
    """
    Customized ArgumentParser class to improve some error messages and prevent
    SystemExit in several occasions, as SystemExit is unacceptable when a
    command is called programmatically.
    """
    def __init__(self, **kwargs):
        self.missing_args_message = kwargs.pop("missing_args_message", None)
        self.called_from_command_line = kwargs.pop("called_from_command_line", None)
        super().__init__(**kwargs)

    def parse_args(self, args=None, namespace=None):
        # Catch missing argument for a better error message
        if (self.missing_args_message and
                not (args or any(not arg.startswith("-") for arg in args))):
            self.error(self.missing_args_message)
        return super().parse_args(args, namespace)

    def error(self, message):
        if self.called_from_command_line:
            super().error(message)
        else:
            raise CommandError("Error: %s" % message)


class RESTfulFalconHelpFormatter(HelpFormatter):
    """
    Customized formatter so that command-specific arguments appear in the
    --help output before arguments common to all commands.
    """
    show_last = {
        "--version", "--verbosity", "--traceback", "--settings", "--pythonpath"
    }

    def _reordered_actions(self, actions):
        return sorted(
            actions,
            key=lambda a: set(a.option_strings) & self.show_last != set()
        )


class OutputWrapper(TextIOBase):
    """
    Wrapper around stdout/stderr
    """
    @property
    def style_func(self):
        return self._style_func

    @style_func.setter
    def style_func(self, style_func):
        if style_func and self.isatty():
            self._style_func = style_func
        else:
            self._style_func = lambda x: x

    def __init__(self, out, style_func=None, ending="\n"):
        self._out = out
        self._style_func = None
        self.style_func = style_func
        self.ending = ending
        super(TextIOBase, self).__init__()

    def __getattr__(self, name):
        return getattr(self._out, name)

    def isatty(self):
        return hasattr(self._out, "isatty") and self._out.isatty()

    def write(self, msg, style_func=None, ending=None):
        ending = self.ending if ending is None else ending
        if ending and not msg.endswith(ending):
            msg += ending
        style_func = style_func or self.style_func
        self._out.write(style_func(msg))


class CommandRegistry(type):
    def __new__(mcs, name, bases, dct):
        cls = super(CommandRegistry, mcs).__new__(mcs, name, bases, dct)
        name = dct.get("name")
        if name:
            COMMANDS[name] = cls
        return cls


class BaseCommand(object, metaclass=CommandRegistry):
    """
    The base class from which all management commands ultimately
    derive.

    Use this class if you want access to all of the mechanisms which
    parse the command-line arguments and work out what code to call in
    response; if you don't need to change any of that behavior,
    consider using one of the subclasses defined in this file.

    If you are interested in overriding/customizing various aspects of
    the command-parsing and -execution behavior, the normal flow works
    as follows:

    1. ``restful-falcon-admin`` or ``manage.py`` loads the command class
       and calls its ``run_from_argv()`` method.

    2. The ``run_from_argv()`` method calls ``create_parser()`` to get
       an ``ArgumentParser`` for the arguments, parses them, performs
       any environment changes requested by options like
       ``pythonpath``, and then calls the ``execute()`` method,
       passing the parsed arguments.

    3. The ``execute()`` method attempts to carry out the command by
       calling the ``handle()`` method with the parsed arguments; any
       output produced by ``handle()`` will be printed to standard
       output and, if the command is intended to produce a block of
       SQL statements, will be wrapped in ``BEGIN`` and ``COMMIT``.

    4. If ``handle()`` or ``execute()`` raised any exception (e.g.
       ``CommandError``), ``run_from_argv()`` will  instead print an error
       message to ``stderr``.

    Thus, the ``handle()`` method is typically the starting point for
    subclasses; many built-in commands and command types either place
    all of their logic in ``handle()``, or perform some additional
    parsing work in ``handle()`` and then delegate from it to more
    specialized methods as needed.

    Several attributes affect behavior at various steps along the way:

    ``help``
        A short description of the command, which will be printed in
        help messages.

    ``stealth_options``
        A tuple of any options the command uses which aren't defined by the
        argument parser.
    """
    # Metadata about this command.
    help = ""

    # Configuration shortcuts that alter various logic.
    _called_from_command_line = False
    # Arguments, common to all commands, which aren't defined by the argument
    # parser.
    base_stealth_options = ("skip_checks", "stderr", "stdout")
    # Command-specific options not defined by the argument parser.
    stealth_options = ()

    def __init__(self, stdout=None, stderr=None):
        self.stdout = OutputWrapper(stdout or sys.stdout)
        self.stderr = OutputWrapper(stderr or sys.stderr)

    # noinspection PyMethodMayBeStatic
    def get_version(self):
        """
        Return the RESTful-falcon version, which should be correct for all
        built-in RESTful-falcon commands. User-supplied commands can override
        this method to return their own version.
        """
        return restful_falcon.get_version()

    def create_parser(self, prog_name, subcommand):
        """
        Create and return the ``ArgumentParser`` which will be used to
        parse the arguments to this command.
        """
        if ".py" in prog_name:
            prog_name = "python {}".format(os.path.basename(prog_name))
        parser = CommandParser(
            prog="%s %s" % (prog_name, subcommand),
            description=self.help or None,
            formatter_class=RESTfulFalconHelpFormatter,
            missing_args_message=getattr(self, "missing_args_message", None),
            called_from_command_line=getattr(self, "_called_from_command_line", None),
        )
        parser.add_argument("--version", action="version", version=self.get_version())
        parser.add_argument(
            "-v", "--verbosity", action="store", dest="verbosity", default=1,
            type=int, choices=[0, 1, 2, 3],
            help="Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output",
        )
        parser.add_argument(
            "--pythonpath",
            help='A directory to add to the Python path, e.g. "/home/projects/myproject".',
        )
        parser.add_argument("--traceback", action="store_true", help="Raise on CommandError exceptions")

        self.add_arguments(parser)
        return parser

    def add_arguments(self, parser):
        """
        Entry point for subclassed commands to add custom arguments.
        """
        pass

    def print_help(self, prog_name, subcommand):
        """
        Print the help message for this command, derived from
        ``self.usage()``.
        """
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help()

    def run_from_argv(self, argv):
        """
        Set up any environment changes requested, then run this command. If the
        command raises a ``CommandError``, intercept it and print it sensibly
        to stderr. If the ``--traceback`` option is present or the raised
        ``Exception`` is not ``CommandError``, raise it.
        """
        self._called_from_command_line = True
        parser = self.create_parser(argv[0], argv[1])

        options = parser.parse_args(argv[2:])
        cmd_options = vars(options)
        # Move positional args out of options to mimic legacy optparse
        args = cmd_options.pop("args", ())
        try:
            self.execute(*args, **cmd_options)
        except Exception as e:
            if options.traceback or not isinstance(e, CommandError):
                raise

            # SystemCheckError takes care of its own formatting.
            if isinstance(e, SystemCheckError):
                self.stderr.write(str(e), lambda x: x)
            else:
                self.stderr.write("%s: %s" % (e.__class__.__name__, e))
            sys.exit(1)

    def execute(self, *args, **options):
        return self.handle(*args, **options)

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement
        this method.
        """
        raise NotImplementedError("subclasses of BaseCommand must provide a handle() method")
