## manage.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("RESTFUL_FALCON_CONFIG", "${project}.configuration")
    try:
        from restful_falcon.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import RESTful-falcon. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
