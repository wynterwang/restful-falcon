## router.py
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from restful_falcon.core.router import Router

"""
The main router definition of `${project}` project.

There are two types of routes can be defined:
    1) route
    Associate a templatized URI path with a resource;
    2) static route
    Add a route to a directory of static files.

How to define `route`:
    Construct a Router with the `routes` keyword argument, which defines
    a routes list and every route is a dict object. There are two methods
    to build a route.
    1) Using a dict object which contains `uri_template`, `resource`|`router`,
       and `suffix` keywords, directly;
    2) Using function `restful_falcon.core.router.route`.

How to define `static route`:
    Construct a Router with the `static_routes` keyword argument, which defines
    a static routes list and every route is a dict object. There are two methods
    to build a static route.
    1) Using a dict object which contains `prefix`, `directory`|`router`,
       `downloadable` and `fallback_filename` keywords, directly;
    2) Using function `restful_falcon.core.router.static_route`.
"""
router = Router(routes=[

])
