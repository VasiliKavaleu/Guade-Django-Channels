"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.sessions import SessionMiddlewareStack # для подключения сессий SessionMiddlewareStack = CookieMiddleware + SessionMiddleware т.е. CookieMiddleware(SessionMiddleware())
from channels.auth import AuthMiddlewareStack # для подключения авторизации AuthMiddlewareStack = CookieMiddleware + SessionMiddleware + AuthMiddleware

from chat.routing import websocket_urls
from chat.middleware import SimpleMiddlewareStack # custom middleware SimpleMiddlewareStack = AuthMiddlewareStack + SimpleMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urls,
        )
    )
})
