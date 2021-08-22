# RESTful-falcon

      ____  _____ ____ _____ __       _       _____     _                 
    |  _ \| ____/ ___|_   _/ _|_   _| |     |  ___|_ _| | ___ ___  _ __  
    | |_) |  _| \___ \ | || |_| | | | |_____| |_ / _` | |/ __/ _ \| '_ \ 
    |  _ <| |___ ___) || ||  _| |_| | |_____|  _| (_| | | (_| (_) | | | |
    |_| \_\_____|____/ |_||_|  \__,_|_|     |_|  \__,_|_|\___\___/|_| |_|


## How to build

```bash
$ git clone https://github.com/wynterwang/restful-falcon.git
$ cd restful-falcon
$ python setup.py bdist_wheel
```

## How to use
### 1. Configure environment
```bash
$ virtualenv --python=python36 example_venv
$ source example_venv/bin/activate
(example_venv)$ pip install restful_falcon-x.y.z-py3-none-any.whl
```

### 2. Create example project
```bash
(example_venv)$ restful-falcon-admin startproject example
(example_venv)$ tree ./
./
├── api                             # API目录
│   └── schema                      # API参数校验定义目录
├── db                              # DB目录
│   ├── migration                   # Model版本目录
│   │   ├── env.py
│   │   ├── README
│   │   ├── script.py.mako
│   │   └── versions
│   └── model                       # Model定义目录
├── etc                             # 配置文件目录
│   ├── alembic.ini
│   ├── conf.d
│   └── example.conf
├── example                         # 项目定义目录
│   ├── application.py
│   ├── configuration.py
│   ├── __init__.py
│   └── router.py
└── manage.py                       # 项目管理脚本
```

### 3. Configure database connection
```bash
(example_venv)$ vi ./etc/example.conf
```
```json
...
"db": {
    "url": "mysql+pymysql://root:@localhost:3306/example",
    "options": {
        "strategy": "threadlocal",
        "encoding": "utf-8",
        "echo": true,
        "pool_size": 10,
        "pool_timeout": 30
    }
},
...
```
*Notes:
    1) More configuration for db to see docstring of `sqlalchemy.engine.create_engine`;
    2) The driver (e.g., driver is `pymysql` in this example) in url should be installed by yourself.*

### 4. Create a model
```bash
(example_venv)$ vi ./db/user.py
```
```python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from restful_falcon.core.db.model import Model
from restful_falcon.core.db.model import Column
from restful_falcon.core.db.mixin import IdAndTimeColumnsMixin
from restful_falcon.core.db.type import String


class User(Model, IdAndTimeColumnsMixin):
    name = Column(String(64), nullable=False)
    address = Column(String(256), nullable=True)
```
### 5. Run database migration
#### 1) Generate migration script
```bash
(example_venv)$ python manage.py alembic revision --autogenerate -m "init"
  Generating /app/example/db/migration/versions/cb0219206559_init.py ...  done 
```
#### 2) Run migration script
```bash
(example_venv)$ python manage.py alembic upgrade head
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> cb0219206559, init
```

### 6. Create an api
```bash
(example_venv)$ vi ./api/user.py
```
```python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from restful_falcon.core.controller.base import Resource
from restful_falcon.core.controller.mixin import ResourceOperatesMixin
from db.model.user import User


class UserResource(Resource, ResourceOperatesMixin):
    resource_model = User
```
### 7. Configure router
```bash
(example_venv)$ vi ./example/router.py
```
```python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from restful_falcon.core.router import Router
from restful_falcon.core.router import route
from api.user import UserResource


router = Router(routes=[
    route("/users", UserResource()),
    route("/users/{rid:int}", UserResource(), suffix="item")
])
```
### 8. Run server
```bash
(example_venv)$ python manage.py runserver 0.0.0.0:8080
```
