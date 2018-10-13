# -*- coding: utf-8 -*-

from urllib import parse
from aiohttp import web
import traceback
import asyncio
import inspect
import logging

from utils.apis import APIError, APIBadRequest, APIMissingParams
import web.middleware as middleware

app = web.Application(middlewares=middleware.middlewares, client_max_size=(1024 ** 2) * 32)


def func_args_filter(func, _filter):
    """Filter the function args list with the given filter

    Args:
        func: (function) Detect the args from the function
        _filter: (function) Args filter

    Returns:
        tuple: Filtered args list
    """
    params = inspect.signature(func).parameters
    args = [name
            for (name, param) in params.items()
            if _filter(param)]
    return tuple(args)


class HandleRequest:
    def __init__(self, func):
        """Init class HandleRequest

        Args:
            func: (function) Handler function
        """
        self.func = func
        self.named_args = func_args_filter(func, lambda param: param.kind == inspect.Parameter.KEYWORD_ONLY)
        self.required_args = func_args_filter(func,
            lambda param: param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty)
        self.has_var_args = len(func_args_filter(func, lambda param: param.kind == inspect.Parameter.VAR_KEYWORD)) > 0
        try:
            self.wrapper_request_required = func.__require_request__
        except AttributeError:
            self.wrapper_request_required = False

    @staticmethod
    async def get_request_params(request):
        """Get request params or payload from `request`

        Args:
            request: (aiohttp.web.Request) Request instance

        Returns:
            dict: Request params or payload

        Raises:
            APIBadRequest: An error occurred if the request body is invalid
        """
        kw = None
        if request.method == 'POST':
            if not request.content_type:
                raise APIBadRequest('Missing Content-Type.')
            ct = request.content_type.lower()
            if ct.startswith('application/json') or ct.startswith('application/csp-report'):
                params = await request.json()
                if not isinstance(params, dict):
                    raise APIBadRequest('JSON body must be object.')
                kw = dict(**params)
            elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                params = await request.post()
                kw = dict(**params)
            else:
                raise APIBadRequest(f'Unsupported Content-Type: {request.content_type}')

            # replace the character that python does not allow to be appear in variable name
            kw = {k.replace('-', '_'): v for (k, v) in kw.items()}
        elif request.method == 'GET':
            qs = request.query_string
            if qs:
                kw = dict()
                for k, v in parse.parse_qs(qs, True).items():
                    kw[k] = v[0]
        if kw is None:
            kw = dict(**request.match_info)
        return kw

    def filter_params(self, kw, request):
        """Filter and check the required request data for handler function

        Args:
            kw: (dict) Request data
            request: (aiohttp.web.Request) Request instance

        Returns:
            dict: Request data needed by the handler

        Raises:
            APIMissingParams: An error occurred if the params is missing
        """
        # copy the args needed by the handler
        if not self.has_var_args and len(self.named_args):
            copy = dict()
            for name in self.named_args:
                if name in kw:
                    copy[name] = kw[name]
            kw = copy
        for k, v in request.match_info.items():
            if k in kw:
                logging.warning(f'Duplicate arg name in named arg and kw args: {k}')
            kw[k] = v
        if 'request' in self.named_args:
            kw['request'] = request
        # check the required args
        for name in self.required_args:
            if name not in kw:
                raise APIMissingParams(name)
        return kw

    async def __call__(self, request):
        """Call the handler function
        """
        try:
            kw = dict()
            if self.has_var_args or len(self.required_args) or len(self.named_args):
                kw = await self.get_request_params(request)
            kw = self.filter_params(kw, request)
            logging.debug(f'call with args: {str(kw)}')
            if self.wrapper_request_required:
                wrapper_request = request
                resp = await self.func(wrapper_request, **kw)
            else:
                resp = await self.func(**kw)
        except APIError as e:
            return web.json_response(dict(error=e.error, msg=e.msg), status=400)
        except Exception:
            logging.error(traceback.format_exc())
            return web.json_response(dict(error='server:server_internal_error'), status=500)
        return resp


def add_route(method, path, func):
    """Add a route to `app`

    Args:
        method: (str) Request method
        path: (str) Request path
        func: (function) Request handler
    """
    if not asyncio.iscoroutinefunction(func) and not inspect.isgeneratorfunction(func):
        func = asyncio.coroutine(func)
    logging.info(
        f'Add route {method.upper()} {path} => {func.__name__}({", ".join(inspect.signature(func).parameters.keys())})')
    app.router.add_route(method, path, HandleRequest(func))


def decorator_factory(method):
    """Request method decorator factory

    Args:
        method: (str) Request method

    Returns:
        function: Request method decorator
    """

    def router(path):
        def decorator(func):
            add_route(method, path, func)
            return func

        return decorator

    return router


# define request method decorator
get = decorator_factory('get')
post = decorator_factory('post')


def init_coroweb():
    pass
