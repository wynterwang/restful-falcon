# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/2"
from __future__ import absolute_import

import re
import sys
import errno
import socket

from datetime import datetime
from restful_falcon.core.management.base import BaseCommand
from restful_falcon.core.management.base import CommandError

naiveip_re = re.compile(r"""^(?:
(?P<addr>
    (?P<ipv4>\d{1,3}(?:\.\d{1,3}){3}) |         # IPv4 address
    (?P<ipv6>\[[a-fA-F0-9:]+\]) |               # IPv6 address
    (?P<fqdn>[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*) # FQDN
):)?(?P<port>\d+)$""", re.X)


class RunServerCommand(BaseCommand):
    name = "runserver"
    help = "Starts a lightweight Web server for development."

    # Validation is called explicitly each time the server is reloaded.
    stealth_options = ("shutdown_message",)

    default_addr = "127.0.0.1"
    default_addr_ipv6 = "::1"
    default_port = "8000"

    def add_arguments(self, parser):
        parser.add_argument(
            "addrport", nargs="?",
            help="Optional port number, or ipaddr:port"
        )

    def handle(self, *args, **options):
        if not options["addrport"]:
            self.addr = self.default_addr
            self.port = self.default_port
        else:
            m = re.match(naiveip_re, options["addrport"])
            if m is None:
                raise CommandError('"%s" is not a valid port number '
                                   'or address:port pair.' % options["addrport"])
            self.addr, _ipv4, _ipv6, _fqdn, self.port = m.groups()
            if not self.port.isdigit():
                raise CommandError("%r is not a valid port number." % self.port)
        self.run(**options)

    def run(self, **options):
        # 'shutdown_message' is a stealth option.
        shutdown_message = options.get("shutdown_message", "")
        quit_command = "CTRL-BREAK" if sys.platform == "win32" else "CONTROL-C"

        now = datetime.now().strftime('%B %d, %Y - %X')
        self.stdout.write(now)
        self.stdout.write((
                              "RESTful-falcon version %(version)s\n"
                              "Starting development server at http://%(addr)s:%(port)s/\n"
                              "Quit the server with %(quit_command)s.\n"
                          ) % {
                              "version": self.get_version(),
                              "addr": '[%s]' % self.addr,
                              "port": self.port,
                              "quit_command": quit_command,
                          })

        try:
            from restful_falcon.core.config import CONF
            from restful_falcon.core.app import Application

            application = Application(CONF)
            application.run(host=self.addr, port=int(self.port))
        except socket.error as e:
            # Use helpful error messages instead of ugly tracebacks.
            errors = {
                errno.EACCES: "You don't have permission to access that port.",
                errno.EADDRINUSE: "That port is already in use.",
                errno.EADDRNOTAVAIL: "That IP address can't be assigned to.",
            }
            try:
                error_text = errors[e.errno]
            except KeyError:
                error_text = e
            self.stderr.write("Error: %s" % error_text)
            # Need to use an OS exit because sys.exit doesn't work in a thread
            sys.exit(1)
        except KeyboardInterrupt:
            if shutdown_message:
                self.stdout.write(shutdown_message)
            sys.exit(0)
