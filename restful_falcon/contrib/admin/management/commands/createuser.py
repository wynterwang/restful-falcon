# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/23"
from __future__ import absolute_import

import getpass

from restful_falcon.contrib.admin.db.model.user import AuthUser
from restful_falcon.core.management.base import BaseCommand
from restful_falcon.core.management.base import CommandError
from restful_falcon.util.crypt import make_password


class CreateUserCommand(BaseCommand):
    name = "createuser"
    help = "Used to create a user."

    @staticmethod
    def _get_password(prompt="Password: "):
        password = getpass.getpass(prompt=prompt)
        if not password:
            raise CommandError("aborted")
        return password

    def add_arguments(self, parser):
        parser.add_argument(
            "--username", action="store", dest="username", default=None,
            help="Specifies the login for the user.",
        )
        parser.add_argument(
            "--admin", action="store_true", dest="admin", default=True,
            help="Whether the user is an administrator"
        )
        parser.add_argument(
            "--system", action="store_true", dest="system", default=False,
            help="Whether the user is a system account"
        )

    def handle(self, *args, **options):
        username = options["username"]
        admin = options["admin"]
        system = options["system"]
        while username is None:
            username = input("Username: ")
            if not username:
                continue
            if AuthUser.exist(filters=[("username", username)]):
                self.stderr.write("Error: That username is already taken.")
                username = None
        if not username:
            raise CommandError("Username cannot be blank.")

        password = None
        while password is None:
            password = self._get_password()
            password2 = self._get_password("Password (again): ")
            if password != password2:
                self.stderr.write("Error: Your passwords didn't match.")
                password = None
                # Don't validate passwords that don't match.
                continue
            if password.strip() == "":
                self.stderr.write("Error: Blank passwords aren't allowed.")
                password = None
                # Don't validate blank passwords.
                continue
        AuthUser.perform_create({
            "username": username, "password": make_password(password),
            "admin": admin, "system": system
        })
        self.stdout.write("User created successfully.")
