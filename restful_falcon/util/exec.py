# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/4"
from __future__ import absolute_import

import subprocess
import sys
from threading import Timer

__all__ = ["execute"]

DEFAULT_TIMEOUT = 120


def execute(script, activate_venv=False, timeout=DEFAULT_TIMEOUT):
    def timeout_callback(program):
        try:
            program.kill()
        except Exception as e:
            raise e

    if activate_venv:
        if not hasattr(sys, "real_prefix"):
            raise RuntimeError(
                "Current execute environment is not a virtual environment"
            )
        if sys.platform != "win32":
            activate_script = "source {}/bin/activate\n".format(sys.prefix)
        else:
            activate_script = "{}\\Scripts\\activate\r\n".format(sys.prefix)
        script = activate_script + script
    executor = subprocess.Popen(script, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timer = Timer(timeout, timeout_callback, [executor])
    timer.start()
    try:
        stdout, stderr = executor.communicate()
        if stdout:
            stdout = stdout.decode(encoding="utf-8")
        if stderr:
            stderr = stderr.decode(encoding="utf-8")
        return executor.returncode, stdout, stderr
    finally:
        timer.cancel()
