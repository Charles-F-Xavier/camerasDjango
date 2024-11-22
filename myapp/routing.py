from django.urls import re_path

from myapp.consumers import CameraFeedConsumer

websocket_urlpatterns = [
    re_path(r'ws/$', CameraFeedConsumer.as_asgi()),
]