## configuration.py
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os

from restful_falcon.core.config import init_config


workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONF = init_config(
    conf_file=os.path.join(workspace, "etc/${project}.conf"),
    conf_dir=os.path.join(workspace, "etc/conf.d"),
    workspace=workspace
)
