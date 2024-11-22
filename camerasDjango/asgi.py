"""
ASGI config for camerasDjango project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from myapp.consumers import CameraFeedConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'camerasDjango.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('ws/', CameraFeedConsumer.as_asgi()),
        ]
        )
    ),
})
