# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/1"
from __future__ import absolute_import

import os
import copy
import json

from configobj import ConfigObj
from mako.template import Template
from restful_falcon.util.exec import execute
from restful_falcon.core.management.base import BaseCommand
from restful_falcon.core.constants import DEFAULT_OPTS


ALEMBIC_INIT_SCRIPT = """
cd ${etc_dir}
alembic init ${init_dir} -t ${template}
"""

ALEMBIC_ENV_SETTING = """
import os
import sys
import restful_falcon

sys.path.append("{workspace}")
os.environ.setdefault("RESTFUL_FALCON_CONFIG", "{project}.configuration")
restful_falcon.setup()

from restful_falcon.core.db.model import Model
target_metadata = Model.metadata
"""


class StartProjectCommand(BaseCommand):
    name = "startproject"
    help = (
        "Creates a RESTful-falcon project directory structure for the given project "
        "name in the current directory or optionally in the given directory."
    )

    missing_args_message = "You must provide a project name."

    def add_arguments(self, parser):
        parser.add_argument(
            "project", action="store", help="Name of the restful-falcon project",
        )
        parser.add_argument(
            "-d", "--directory", action="store", dest="directory", default="./",
            help="The directory of the current project",
        )
        parser.add_argument(
            "-t", "--template", action="store", default="generic",
            choices=("generic", "multidb", "pylons"),
            help="Setup template for use with alembic init"
        )

    def init_workspace(self, project, directory):
        if not os.path.isdir(directory):
            raise OSError("'{}' is not a directory".format(directory))
        if not os.access(directory, os.R_OK | os.W_OK | os.X_OK):
            raise PermissionError("No permission to operate directory '{}'".format(directory))
        workspace = os.path.join(directory, project)
        if os.path.exists(workspace):
            raise OSError("The directory '{}' already exists".format(workspace))
        os.makedirs(workspace, mode=0o755)
        for subdir in ["api", "api/schema", "db", "db/model", "etc", "etc/conf.d", project]:
            os.makedirs(os.path.join(workspace, subdir), mode=0o755)
        self.stdout.write("  Creating directory {} ... done".format(workspace))

    def generate_conf_file(self, project, directory):
        conf_file = os.path.join(directory, "{project}/etc/{project}.conf".format(project=project))
        default_opts = copy.deepcopy(DEFAULT_OPTS)
        default_opts["name"] = project
        with open(conf_file, "w") as fd:
            json.dump(default_opts, fd, indent=4)
        self.stdout.write("  Generating {} ... done".format(conf_file))

    def render_template_files(self, project, directory):
        import restful_falcon

        template_dir = os.path.join(
            restful_falcon.__path__[0], "core/template"
        )
        workspace = os.path.join(directory, project)
        kwargs_map = {
            "configuration.py.mako": {
                "project": project
            },
            "manage.py.mako": {
                "project": project
            },
            "router.py.mako": {
                "project": project
            }
        }
        for name in os.listdir(template_dir):
            if not name.endswith(".mako"):
                continue
            template = Template(filename=os.path.join(template_dir, name))
            if name.startswith("manage.py"):
                dst_file = os.path.join(workspace, name.rpartition(".")[0])
            else:
                dst_file = os.path.join(workspace, "{}/{}".format(project, name.rpartition(".")[0]))
            with open(dst_file, "w") as fd:
                fd.write(template.render(**kwargs_map.get(name, {})))
        self.stdout.write("  Rendering python files ... done")

    def generate_alembic_files(self, project, directory, template):
        workspace = os.path.join(directory, project)
        etc_dir = os.path.join(workspace, "etc")
        migration_dir = os.path.join(workspace, "db/migration")
        script = Template(ALEMBIC_INIT_SCRIPT).render(etc_dir=etc_dir, init_dir=migration_dir, template=template)
        code, stdout, stderr = execute(script, activate_venv=True)
        self.stdout.write(stdout or stderr)
        if code == 0:
            self.stdout.write("  Generating alembic ... done")
        else:
            self.stderr.write("  Generating alembic ... failure")

    def revise_alembic_conf_file(self, project, directory):
        workspace = os.path.join(directory, project)
        conf_file = os.path.join(workspace, "etc/alembic.ini")
        config = ConfigObj(conf_file, encoding="utf-8")
        if "sqlalchemy.url" in config["alembic"]:
            config["alembic"]["sqlalchemy.url"] = ""
        if "logger_sqlalchemy" in config:
            config["logger_sqlalchemy"]["handlers"] = "console"
        if "logger_alembic" in config:
            config["logger_alembic"]["handlers"] = "console"
        config.write()
        self.stdout.write("  Revising {} ... done".format(conf_file))

    def revise_alembic_env_file(self, project, directory, template):
        workspace = os.path.join(directory, project)
        env_file = os.path.join(workspace, "db/migration/env.py")
        with open(env_file, "r") as fd:
            content = fd.read()
        if template != "multidb":
            content = content.replace(
                "target_metadata = None", ALEMBIC_ENV_SETTING.format(
                    workspace=workspace, project=project
                ).strip()
            )
        with open(env_file, "w") as fd:
            fd.write(content)
        self.stdout.write("  Revising {} ... done".format(env_file))

    def handle(self, *args, **options):
        project = options["project"]
        directory = os.path.abspath(options["directory"])
        template = options["template"]
        self.init_workspace(project, directory)
        self.generate_conf_file(project, directory)
        self.render_template_files(project, directory)
        self.generate_alembic_files(project, directory, template)
        self.revise_alembic_conf_file(project, directory)
        self.revise_alembic_env_file(project, directory, template)
