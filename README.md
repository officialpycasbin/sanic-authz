# sanic-authz

[![build](https://github.com/officialpycasbin/sanic-authz/actions/workflows/build.yml/badge.svg)](https://github.com/officialpycasbin/sanic-authz/actions/workflows/build.yml)
[![Coverage Status](https://coveralls.io/repos/github/officialpycasbin/sanic-authz/badge.svg)](https://coveralls.io/github/officialpycasbin/sanic-authz)
[![Version](https://img.shields.io/pypi/v/sanic-authz.svg)](https://pypi.org/project/sanic-authz/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/sanic-authz.svg)](https://pypi.org/project/sanic-authz/)
[![Pyversions](https://img.shields.io/pypi/pyversions/sanic-authz.svg)](https://pypi.org/project/sanic-authz/)
[![Download](https://static.pepy.tech/badge/sanic-authz)](https://pypi.org/project/sanic-authz/)
[![Discord](https://img.shields.io/discord/1022748306096537660?logo=discord&label=discord&color=5865F2)](https://discord.gg/S5UjpzGZjN)

sanic-authz is an authorization middleware for [Sanic](https://sanic.dev/en/). It is based on [PyCasbin](https://github.com/casbin/pycasbin).

## Installation
```
pip install sanic-authz
```

## Module Usage:
```python
import casbin
from sanic import Sanic, response
from sanic.request import Request
from sanic_authz.middleware import CasbinAuthMiddleware

app = Sanic("SanicAuthzExample")
enforcer = casbin.Enforcer("rbac_model.conf", "policy.csv")

# Registration middleware
CasbinAuthMiddleware(sanic_app, enforcer)

# CasbinAuthMiddleware is a global middleware.
# The authorization check will be performed automatically on each request.
# You don't need to manually invoke the middleware in your route handlers.
@app.route("/")
async def homepage(request):
    return response.text("Hello, world!")
```

Custom subject_getter:

By default, the middleware extracts user identity from the `X-User` header field. Client requests need to include the X-User header:
```
curl -H "X-User: alice" http://localhost:8000/data
```
You can customize the subject_getter to adapt to different authentication mechanisms. For example, JWT authentication:
```python
def jwt_subject_getter(request: Request) -> str:
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_jwt(token)
    return payload.get("user_id", "anonymous")

CasbinAuthMiddleware(app, enforcer, subject_getter=jwt_subject_getter)
```
session authentication:
```python
def session_subject_getter(request: Request) -> str:
    return request.ctx.session.get("user_id", "anonymous")

CasbinAuthMiddleware(app, enforcer, subject_getter=session_subject_getter)
```

## Documentation

The authorization determines a request based on ``{subject, object, action}``, which means what ``subject`` can perform what ``action`` on what ``object``. In this plugin, the meanings are:

1. ``subject``: the logged-in user name
2. ``object``: the URL path for the web resource like "dataset1/item1"
3. ``action``: HTTP method like GET, POST, PUT, DELETE, or the high-level actions you defined like "read-file", "write-blog"

For how to write authorization policy and other details, please refer to [the PyCasbin's documentation](https://github.com/casbin/pycasbin).

### Getting Help

- [PyCasbin](https://github.com/casbin/pycasbin)

### License

This project is licensed under the [Apache 2.0 license](LICENSE).
