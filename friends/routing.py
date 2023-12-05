from django.urls import re_path

from friends.consumers import LocationConsumer

websocket_urlpatterns = [
    re_path(r'ws/$', LocationConsumer.as_asgi()),
]