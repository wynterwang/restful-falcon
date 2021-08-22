# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/7"
from setuptools import setup
from setuptools import find_packages

from restful_falcon.util.version import get_main_version

setup(
    name="restful-falcon",
    version=get_main_version(),
    description="RESTful falcon framework",
    long_description="RESTful falcon framework.",
    license="MIT Licence",

    url="http://github.com/wynterwang/restful-falcon.git",
    author="wynterwang",
    author_email="wynterwang@foxmail.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[
        "falcon==2.0.0",
        "SQLAlchemy==1.3.18",
        "Mako==1.1.3",
        "alembic==1.4.2",
        "cacheout==0.11.2",
        "redis==3.5.3",
        "jsonschema==3.2.0",
        "configobj==5.0.6"
    ],
    entry_points={
        "console_scripts": [
            "restful-falcon-admin = restful_falcon.cmd.restful_falcon_admin:main"
        ]
    },
    zip_safe=False
)
