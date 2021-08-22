# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/15"
from __future__ import absolute_import

import sys
import threading
from collections import Counter
from collections import OrderedDict

import os

from restful_falcon.apps.config import AppConfig

__all__ = ["Apps", "apps"]


class Apps:
    """
    A registry that stores the configuration of installed applications.
    """

    def __init__(self, installed_apps=()):
        # installed_apps is set to None when creating the master registry
        # because it cannot be populated at that point. Other registries must
        # provide a list of installed apps and are populated immediately.
        if installed_apps is None and hasattr(sys.modules[__name__], "apps"):
            raise RuntimeError("You must supply an installed_apps argument.")

        # Mapping of labels to AppConfig instances for installed apps.
        self.app_configs = OrderedDict()

        # Stack of app_configs. Used to store the current state in
        # set_available_apps and set_installed_apps.
        self.stored_app_configs = []

        # Whether the registry is populated.
        self.apps_ready = self.models_ready = self.ready = False

        # Lock for thread-safe population.
        self._lock = threading.RLock()
        self.loading = False

        # Populate apps and models, unless it's the master registry.
        if installed_apps is not None:
            self.populate(installed_apps)

    def populate(self, workspace, installed_apps=None):
        """
        Load application configurations and models.

        Import each application module and then each model module.

        It is thread-safe and idempotent, but not reentrant.
        """
        if self.ready:
            return

        # populate() might be called by two threads in parallel on servers
        # that create threads before initializing the WSGI callable.
        with self._lock:
            if self.ready:
                return

            # An RLock prevents other threads from entering this section. The
            # compare and set operation below is atomic.
            if self.loading:
                # Prevent reentrant calls to avoid running AppConfig.ready()
                # methods twice.
                raise RuntimeError("populate() isn't reentrant")
            self.loading = True

            # Phase 1: initialize app configs and import app modules.
            for entry in installed_apps:
                if isinstance(entry, AppConfig):
                    app_config = entry
                else:
                    app_config = AppConfig.create(entry)
                if app_config.label in self.app_configs:
                    raise ValueError(
                        "Application labels aren't unique, duplicates: {}".format(app_config.label)
                    )

                self.app_configs[app_config.label] = app_config
                app_config.apps = self

            # Check for duplicate app names.
            counts = Counter(app_config.name for app_config in self.app_configs.values())
            duplicates = [name for name, count in counts.most_common() if count > 1]
            if duplicates:
                raise ValueError(
                    "Application names aren't unique, duplicates: %s".format(", ".join(duplicates))
                )

            self.apps_ready = True

            # Phase 2: import models modules.
            for app_config in self.app_configs.values():
                app_config.import_models()
            AppConfig.import_models_from(
                os.path.join(workspace, "db/model")
            )

            self.models_ready = True

            # Phase 3: run ready() methods of app configs.
            for app_config in self.get_app_configs():
                app_config.ready()

            self.ready = True

    def check_apps_ready(self):
        """
        Raise an exception if all apps haven't been imported yet.
        """
        if not self.apps_ready:
            raise RuntimeError("Apps aren't loaded yet.")

    def check_models_ready(self):
        """
        Raise an exception if all models haven't been imported yet.
        """
        if not self.models_ready:
            raise RuntimeError("Models aren't loaded yet.")

    def get_app_configs(self):
        """
        Import applications and return an iterable of app configs.
        """
        self.check_apps_ready()
        return self.app_configs.values()

    def get_app_config(self, app_label):
        """
        Import applications and returns an app config for the given label.

        Raise LookupError if no application exists with this label.
        """
        self.check_apps_ready()
        try:
            return self.app_configs[app_label]
        except KeyError:
            message = "No installed app with label '%s'." % app_label
            for app_config in self.get_app_configs():
                if app_config.name == app_label:
                    message += " Did you mean '%s'?" % app_config.label
                    break
            raise LookupError(message)

    def is_installed(self, app_name):
        """
        Check whether an application with this name exists in the registry.

        app_name is the full name of the app e.g. 'restful_falcon.contrib.admin'.
        """
        self.check_apps_ready()
        return any(ac.name == app_name for ac in self.app_configs.values())


apps = Apps(installed_apps=None)
