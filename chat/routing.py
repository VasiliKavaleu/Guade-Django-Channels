from django.conf.urls import url

from .consumers import (
    ChatConsumer, AsyncChatConsumer, BaseSyncConsumer, BaseAsyncConsumer, ChatJsonConsumer,
    SyncChatConsumer
)

websocket_urls = [
    url(r'^ws/chat/$', ChatConsumer.as_asgi()),
    url(r'^ws/basesync/$', BaseSyncConsumer.as_asgi()),
    url(r'^ws/baseasync/$', BaseAsyncConsumer.as_asgi()),
    url(r'^ws/json/$', ChatJsonConsumer.as_asgi()),

    url(r'^ws/sync_chat/(?P<room_name>\w+)/$', SyncChatConsumer.as_asgi()),
    url(r'^ws/async_chat/(?P<room_name>\w+)/$', AsyncChatConsumer.as_asgi()),
]
