import json

from channels.generic.websocket import (
    AsyncJsonWebsocketConsumer, JsonWebsocketConsumer, 
    WebsocketConsumer, AsyncWebsocketConsumer, AsyncConsumer
    )
from channels.consumer import SyncConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync


# scope аналог словарю request во view - в котором содержится вся инфа запроса
# доступен внутри класса консьюмера как self.scope

# если нет необходимости чтобы процессы общались между собой, можно не использовать channel_layers
# channel_layers - полностью асинхронный, для использования в синхронном коде 
# необходимо использовать с async_to_sync : async_to_sync(channel_layer.group_send)("chat", {})
# где channel_layer.group_send метод который используем, ("chat", {}) параметры этого метода

# пользователь устанавливает соединение - создается инстанс консьюмера,
# одно соединение - на один консьюмер и когда соединение установлено внутри класса 
# доступен атрибут self.channel_name - уникалный индификатор вашего соединения между приложением и клиентом
# используя self.channel_name можем коммуникацировать с клиентом

# через channel_layer происходит взаимодействие с группой пользователей

# self.channel_layer.send(channel_name, {}), channel_name уникальное имя канала в который хотим что-то отправить
# {} данные которые хотим что-то отправить

# создание группы self.channel_layer.group_add(group_name, self.channel_name),
# где group_name - уникальный номер группы, self.channel_name уникальное имя соединения который установил пользователь
# все эти действия происходят в момент установления соединения websocket_connect
# при разрыве соединения (в websocket_disconnect) необходимо вызвать метод - self.channel_layer.group_discard(group_name, self.channel_name)
# для того чтобы удалить соединение из этой группы

# после установки соединения и создания группы можем посылать сообщения в группу - self.channel_layer.group_send(group_name, {}) и всем 
# пользователям кто добавлен в эту группу

class SyncChatConsumer(WebsocketConsumer):
    """Пример использованиея channel_layer в синхронном консьюмере"""
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"] # получаем имя чата из url
        # добавляемся в группу с именем self.room_name
        async_to_sync(self.channel_layer.group_add)(self.room_name, self.channel_name) # уникальное имя канала с определенным поьзователем записывается в self.channel_name
        self.accept() 
    
    def disconnect(self, code):
        # разрываем соединение, выходим из группы
        async_to_sync(self.channel_layer.group_discard)(self.room_name, self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        async_to_sync(self.channel_layer.group_send)(  # отсылаем сообщение в channel_layer, а из channel_layer отправляется всем пользователям в группе под имененм self.room_name
            self.room_name, 
            {
                "type": "chat.message", # должны создать метод в текущем консьюмере обрабатывающий этот тип сообщения и название этого обработчика должно быть 
                                        # и название этого обработчика должно быть как и название типа только вместо точки нижнее подчеркивание
                "text": text_data  
            }                           
        )

    def chat_message(self, event): # этот метод принимает event который и содержит словарь {"type": "chat.message", "text": text_data}
        self.send(text_data=event["text"])


class AsyncChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept() 
    
    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        await self.channel_layer.group_send(  
            self.room_name, 
            {
                "type": "chat.message",
                "text": text_data  
            }                           
        )

    async def chat_message(self, event):
        await self.send(text_data=event["text"])





class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept() # разрешение установки соединения
    
    def disconnect(self, code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        json_data = json.loads(text_data) # text_data - входящие данные
        message = json_data['message'] # получение из входящих данных инф - message
        self.send(
            text_data=json.dumps({
                'message': message
            })
        ) # send - отправка данных (отправляет text_data ), которы принимает text_data в формате json


# class AsyncChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept() 
    
#     async def disconnect(self, code):
#         pass

#     async def receive(self, text_data=None, bytes_data=None):
#         json_data = json.loads(text_data)
#         message = json_data['message']
#         await self.send(
#             text_data=json.dumps({
#                 'message': message
#             })
#         )


class BaseSyncConsumer(SyncConsumer): # базовый консьюмер
    def websocket_connect(self, event):
        self.send({
            "type": "websocket.accept"
        })

    def websocket_receive(self, event): 
        # event - это dict где первым ключом должен быть
        # type c типом сообщения с которым хотим работать (e. websocket.accept)
        # EVENT = {'type': 'websocket.receive', 'text': '{"message": "Hi"}'}
        # спецификация ASGI разрешает послать типы text or bytes
        self.send({
            "type": "websocket.send",
            "text": event['text']
        })

    def websocket_disconnect(self):
        raise StopConsumer


class BaseAsyncConsumer(AsyncConsumer): # базовый консьюмер - в котором нужно определять как происходит закрытие в websocket_disconnect
    async def websocket_connect(self, event):
        await self.send({
            "type": "websocket.accept"
        })

    async def websocket_receive(self, event): 
        await self.send({
            "type": "websocket.send",
            "text": event['text']
        })

class ChatJsonConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept() 
    
    def disconnect(self, code):
        pass

    def receive_json(self, content):
        self.send_json(
            content=content
        )

class AsyncChatJsonConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept() 
    
    def disconnect(self, code):
        pass

    async def receive_json(self, content):
        await self.send_json(
            content=content
        )