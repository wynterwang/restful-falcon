# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/15"
from __future__ import absolute_import

import traceback
from logging import getLogger
from runpy import run_path

import os

from restful_falcon.util.file import list_files
from restful_falcon.util.module import import_cls
from restful_falcon.util.module import import_module

__all__ = ["AppConfig"]

logger = getLogger(__name__)


class AppConfig:
    """
    Class representing a Restful-falcon application and its configuration.
    """

    def __init__(self, app_name, app_module):
        # Full Python path to the application e.g. "restful_falcon.contrib.admin".
        self.name = app_name

        # Root module for the application e.g. <module "restful_falcon.contrib.admin"
        # from "restful_falcon/contrib/admin/__init__.py">.
        self.module = app_module

        # Reference to the Apps registry that holds this AppConfig. Set by the
        # registry when it registers the AppConfig instance.
        self.apps = None

        # The following attributes could be defined at the class level in a
        # subclass, hence the test-and-set pattern.

        # Last component of the Python path to the application e.g. "admin".
        # This value must be unique across a Django project.
        if not hasattr(self, "label"):
            self.label = app_name.rpartition(".")[2]

        # Human-readable name for the application e.g. "Admin".
        if not hasattr(self, "verbose_name"):
            self.verbose_name = self.label.title()

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.label)

    @classmethod
    def create(cls, entry):
        """
        Factory that creates an app config from an entry in installed_apps.
        """
        module = import_module(entry)
        if isinstance(module, AppConfig):
            return cls(entry, module)
        entry = module.default_app_config
        _cls = import_cls(entry)
        try:
            app_name = _cls.name
        except AttributeError:
            raise AttributeError(
                "'{}' must supply a name attribute".format(entry)
            )
        try:
            app_module = import_module(app_name)
        except ImportError:
            raise ImportError(
                "Cannot import '{}'".format(app_name)
            )
        return _cls(app_name, app_module)

    @classmethod
    def import_models_from(cls, models_dir):
        for file in list_files(models_dir, recursive=True):
            # noinspection PyBroadException
            try:
                if not file.endswith(".py"):
                    continue
                run_path(file)
            except Exception as e:
                logger.warning(str(e))
                logger.warning(traceback.format_exc())

    def import_models(self):
        models_dir = os.path.abspath(
            os.path.join(os.path.dirname(self.module.__file__), "db/model")
        )
        return self.import_models_from(models_dir)

    def ready(self):
        """
        Override this method in subclasses to run code when Re starts.
        """
