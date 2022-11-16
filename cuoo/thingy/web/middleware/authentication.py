import os

from aiohttp.web import middleware, HTTPUnauthorized


class Authentiction:
    @staticmethod
    @middleware
    async def handle(request, handler):
        _token = os.environ.get('AUTH_TOKEN', False)
        if _token:
            try:
                scheme, token = request.headers['Authorization'].strip().split(' ')
            except KeyError or ValueError:
                raise HTTPUnauthorized()

            if scheme.lower() != 'bearer' or token != _token:
                raise HTTPUnauthorized()

        return await handler(request)