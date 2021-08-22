# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/1"
from __future__ import absolute_import

import os

from configobj import ConfigObj
from restful_falcon.util.exec import execute
from restful_falcon.util.wrapper import ignore_errors_except
from restful_falcon.core.management.base import BaseCommand

SUB_COMMANDS = {}


def recover_optional_args(alembic_args, options, prefix="alembic"):
    for name in options:
        if not name.startswith(prefix):
            continue
        mode, _, src_name = name.partition("_")[-1].partition("_")
        mode = int(mode)
        if mode < 1 or mode > 2:
            raise AttributeError("Unknown mode in alembic arg '{}'".format(name))
        src_name = "-" + src_name if mode == 1 else "--" + src_name
        if isinstance(options[name], bool):
            if options[name]:
                alembic_args.append(src_name)
        elif name in options and options[name]:
            if isinstance(options[name], (list, tuple)):
                for value in options[name]:
                    alembic_args.append(src_name)
                    alembic_args.append(value)
            else:
                alembic_args.append(src_name)
                alembic_args.append(options[name])


@ignore_errors_except()
def try_revise_alembic_ini(alembic_ini, db_url):
    config = ConfigObj(alembic_ini, encoding="utf-8")
    if "sqlalchemy.url" in config["alembic"] and not config["alembic"]["sqlalchemy.url"]:
        config["alembic"]["sqlalchemy.url"] = db_url
    config.write()


class AlembicSubCommandRegistry(type):
    def __new__(mcs, name, bases, dct):
        cls = super(AlembicSubCommandRegistry, mcs).__new__(mcs, name, bases, dct)
        if bases != (object,):
            command_name = dct.get("name")
            SUB_COMMANDS[command_name] = cls()
        return cls


class AlembicSubCommand(object, metaclass=AlembicSubCommandRegistry):
    name = None
    help = None

    def add_parser(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.help)
        self.add_arguments(parser)
        parser.set_defaults(func=self.handle)

    def add_arguments(self, parser):
        pass

    def recover_positional_args(self, alembic_args, options):
        pass

    def handle(self, alembic_args, **options):
        alembic_args.append(self.name)
        recover_optional_args(alembic_args, options, prefix="subalembic")
        self.recover_positional_args(alembic_args, options)
        code, stdout, stderr = execute(" ".join(alembic_args), activate_venv=True)
        return stdout or stderr or ""


class AlembicBranches(AlembicSubCommand):
    name = "branches"
    help = " Show current branch points."


class AlembicCurrent(AlembicSubCommand):
    name = "current"
    help = "Display the current revision for a database."


class AlembicDowngrade(AlembicSubCommand):
    name = "downgrade"
    help = "Revert to a previous version."

    def add_arguments(self, parser):
        parser.add_argument(
            "revision", action="store", help="revision identifier",
        )
        parser.add_argument(
            "--sql", action="store_true", dest="subalembic_2_sql",
            help="Don't emit SQL to database - dump to standard output/file instead. See docs on offline mode."
        )
        parser.add_argument(
            "--tag", action="store", dest="subalembic_2_tag",
            help="Arbitrary 'tag' name - can be used by custom env.py scripts."
        )

    def recover_positional_args(self, alembic_args, options):
        alembic_args.append(options["revision"])


class AlembicEdit(AlembicSubCommand):
    name = "edit"
    help = "Edit revision script(s) using $EDITOR."

    def add_arguments(self, parser):
        parser.add_argument(
            "rev", action="store", help="revision identifier",
        )

    def recover_positional_args(self, alembic_args, options):
        alembic_args.append(options["rev"])


class AlembicHeads(AlembicSubCommand):
    name = "heads"
    help = "Show current available heads in the script directory."

    def add_arguments(self, parser):
        parser.add_argument(
            "--resolve-dependencies", action="store", dest="subalembic_2_resolve-dependencies",
            help="Treat dependency versions as down revisions"
        )


class AlembicHistory(AlembicSubCommand):
    name = "history"
    help = "List changeset scripts in chronological order."

    def add_arguments(self, parser):
        parser.add_argument(
            "-r", "--rev-range", action="store", dest="subalembic_2_rev-range",
            help="Specify a revision range; format is [start]:[end]"
        )
        parser.add_argument(
            "-i", "--indicate-current", action="store_true", dest="subalembic_2_indicate-current",
            help="Indicate the current revision"
        )


class AlembicInit(AlembicSubCommand):
    name = "init"
    help = "Initialize a new scripts directory."

    def add_arguments(self, parser):
        parser.add_argument(
            "directory", action="store", help="location of scripts directory",
        )
        parser.add_argument(
            "-t", "--template", action="store", dest="subalembic_2_template",
            help="Setup template for use with 'init'"
        )
        parser.add_argument(
            "--package", action="store_true", dest="subalembic_2_package",
            help="Write empty __init__.py files to the environment and version locations"
        )

    def recover_positional_args(self, alembic_args, options):
        alembic_args.append(options["directory"])


class AlembicListTemplates(AlembicSubCommand):
    name = "list_templates"
    help = "List available templates."


class AlembicMerge(AlembicSubCommand):
    name = "merge"
    help = "Merge two revisions together. Creates a new migration file."

    def add_arguments(self, parser):
        parser.add_argument(
            "revisions", nargs="+", help="one or more revisions, or 'heads' for all heads",
        )
        parser.add_argument(
            "-m", "--message", action="store", dest="subalembic_2_message",
            help="Message string to use with 'revision'"
        )
        parser.add_argument(
            "--branch-label", action="store", dest="subalembic_2_branch-label",
            help="Specify a branch label to apply to the new revision"
        )
        parser.add_argument(
            "--rev-id", action="store", dest="subalembic_2_rev-id",
            help="Specify a hardcoded revision id instead of generating one"
        )

    def recover_positional_args(self, alembic_args, options):
        alembic_args.extend(options["revisions"])


class AlembicRevision(AlembicSubCommand):
    name = "revision"
    help = "Create a new revision file."

    def add_arguments(self, parser):
        parser.add_argument(
            "-m", "--message", action="store", dest="subalembic_2_message",
            help="Message string to use with 'revision'"
        )
        parser.add_argument(
            "--autogenerate", action="store_true", dest="subalembic_2_autogenerate",
            help="Populate revision script with candidate migration operations, based "
                 "on comparison of database to model."
        )
        parser.add_argument(
            "--sql", action="store_true", dest="subalembic_2_sql",
            help="Don't emit SQL to database - dump to standard output/file instead. See docs on offline mode."
        )
        parser.add_argument(
            "--head", action="store", dest="subalembic_2_head",
            help="Specify head revision or <branchname>@head to base new revision on."
        )
        parser.add_argument(
            "--splice", action="store_true", dest="subalembic_2_splice",
            help="Allow a non-head revision as the 'head' to splice onto"
        )
        parser.add_argument(
            "--branch-label", action="store", dest="subalembic_2_branch-label",
            help="Specify a branch label to apply to the new revision"
        )
        parser.add_argument(
            "--version-path", action="store", dest="subalembic_2_version-path",
            help="Specify specific path from config for version file"
        )
        parser.add_argument(
            "--rev-id", action="store", dest="subalembic_2_rev-id",
            help="Specify a hardcoded revision id instead of generating one"
        )
        parser.add_argument(
            "--depends-on", action="store", dest="subalembic_2_depends-on",
            help="Specify one or more revision identifiers which this revision should depend on."
        )


class AlembicShow(AlembicSubCommand):
    name = "show"
    help = "Show the revision(s) denoted by the given symbol."

    def add_arguments(self, parser):
        parser.add_argument(
            "rev", action="store", help="revision identifier",
        )

    def recover_positional_args(self, alembic_args, options):
        alembic_args.append(options["rev"])


class AlembicStamp(AlembicSubCommand):
    name = "stamp"
    help = "'stamp' the revision table with the given revision; don't run any migrations."

    def add_arguments(self, parser):
        parser.add_argument(
            "revisions", nargs="+", help="one or more revisions, or 'heads' for all heads",
        )
        parser.add_argument(
            "--sql", action="store_true", dest="subalembic_2_sql",
            help="Don't emit SQL to database - dump to standard output/file instead. See docs on offline mode."
        )
        parser.add_argument(
            "--tag", action="store", dest="subalembic_2_tag",
            help="Arbitrary 'tag' name - can be used by custom env.py scripts."
        )
        parser.add_argument(
            "--purge", action="store_true", dest="subalembic_2_purge",
            help="Unconditionally erase the version table before stamping"
        )

    def recover_positional_args(self, alembic_args, options):
        alembic_args.extend(options["revisions"])


class AlembicUpgrade(AlembicSubCommand):
    name = "upgrade"
    help = "Upgrade to a later version."

    def add_arguments(self, parser):
        parser.add_argument(
            "revision", action="store", help="revision identifier",
        )
        parser.add_argument(
            "--sql", action="store_true", dest="subalembic_2_sql",
            help="Don't emit SQL to database - dump to standard output/file instead. See docs on offline mode."
        )
        parser.add_argument(
            "--tag", action="store", dest="subalembic_2_tag",
            help="Arbitrary 'tag' name - can be used by custom env.py scripts."
        )

    def recover_positional_args(self, alembic_args, options):
        alembic_args.append(options["revision"])


class AlembicCommand(BaseCommand):
    name = "alembic"
    help = (
        "Alembic provides for the creation, management, and invocation of change management "
        "scripts for a relational database, using SQLAlchemy as the underlying engine."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--raiseerr", action="store_true", dest="alembic_2_raiseerr",
            help="Raise a full stack trace on error"
        )
        parser.add_argument(
            "-c", "--config", action="store", dest="alembic_2_config",
            help='Alternate config file; defaults to value of "etc/alembic.ini"'
        )
        parser.add_argument(
            "-n", "--name", action="store", dest="alembic_2_name",
            help="Name of section in .ini file to use for Alembic config"
        )
        parser.add_argument(
            "-x", action="append", dest="alembic_1_x",
            help="Additional arguments consumed by custom env.py scripts, "
                 "e.g. -x setting1=somesetting -x setting2=somesetting"
        )
        subparsers = parser.add_subparsers()
        for name, command in SUB_COMMANDS.items():
            command.add_parser(subparsers)

    def handle(self, *args, **options):
        from restful_falcon.core.config import CONF

        alembic_args = [self.name]
        recover_optional_args(alembic_args, options)
        if not options.get("alembic_2_config") and hasattr(CONF, "workspace"):
            alembic_args.append("--config")
            alembic_args.append(os.path.join(CONF.workspace, "etc/alembic.ini"))
        if "func" in options:
            if hasattr(CONF, "db"):
                try_revise_alembic_ini(
                    os.path.join(CONF.workspace, "etc/alembic.ini"), CONF.db.url
                )
            self.stdout.write(options["func"](alembic_args, **options))
        else:
            alembic_args.append("--help")
            code, stdout, stderr = execute(" ".join(alembic_args), activate_venv=True)
            self.stdout.write(stdout or stderr)
