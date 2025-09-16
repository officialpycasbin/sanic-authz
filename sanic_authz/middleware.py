# Copyright 2025 The casbin Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import casbin
from functools import wraps
from sanic import Sanic
from sanic.request import Request
from sanic.exceptions import Forbidden


class CasbinAuthMiddleware:
    """
    Sanic aurtorization middleware based on PyCasbin.
    """

    def __init__(self, app: Sanic, enforcer: casbin.Enforcer, subject_getter: callable = None):
        """
        Initialize the middleware.

        :param app: The Sanic app instance.
        :param enforcer: The PyCasbin enforcer instance.
        :param subject_getter: A callable function to get the subject from the request.
                               It should take a `Request` object and return the subject string.
                               If not provided, a default getter is used.
        """
        self.app = app
        self.enforcer = enforcer
        self.subject_getter = subject_getter or self._default_subject_getter

        # Register the middleware to run on each request
        @app.on_request
        async def authorize(request: Request):
            await self._authorize(request)

    def _default_subject_getter(self, request: Request) -> str:
        return request.headers.get("X-User", "anonymous")

    async def _authorize(self, request: Request):
        """
        The core authorization logic that is executed on each request.
        """
        subject = self.subject_getter(request)
        obj = request.path
        act = request.method

        if not self.enforcer.enforce(subject, obj, act):
            raise Forbidden(f"Access Denied: Subject '{subject}' is not authorized to perform '{act}' on '{obj}'.")
