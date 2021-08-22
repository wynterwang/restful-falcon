# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/23"
from __future__ import absolute_import

import getpass

from restful_falcon.contrib.admin.db.model.user import AuthUser
from restful_falcon.core.management.base import BaseCommand
from restful_falcon.core.management.base import CommandError
from restful_falcon.util.crypt import make_password


class ChangePasswordCommand(BaseCommand):
    name = "changepassword"
    help = "Change a user's password for restful_falcon.contrib.auth."

    @staticmethod
    def _get_password(prompt="Password: "):
        password = getpass.getpass(prompt=prompt)
        if not password:
            raise CommandError("aborted")
        return password

    def add_arguments(self, parser):
        parser.add_argument(
            "username", nargs="?", help="Username to change password for; by default, it's the current username.",
        )

    def handle(self, *args, **options):
        username = options["username"] if options["username"] else getpass.getuser()
        if not AuthUser.exist(filters=[("username", username)]):
            raise CommandError("user '{}' does not exist".format(username))
        self.stdout.write("Changing password for user '{}'\n".format(username))

        count, max_reties = 0, 3
        password1, password2 = 1, 2
        while count < max_reties:
            password1 = self._get_password()
            password2 = self._get_password("Password (again): ")
            if password1 == password2:
                break
            self.stdout.write("Passwords do not match. Please try again.\n")
            count += 1
        if count == max_reties:
            raise CommandError("Aborting password change for user '{}' after {} attempts".format(username, count))
        AuthUser.perform_update_by(
            filters=[("username", username)], data={"password": make_password(password1)}
        )
        self.stdout.write("Password changed successfully for user '{}'".format(username))
