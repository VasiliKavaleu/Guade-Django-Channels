from channels.generic.websocket import AsyncJsonWebsocketConsumer


class BaseChatConsumer(AsyncJsonWebsocketConsumer):
    async def _group_send(self, data, event=None):
        data = {"type": "response.proxy", "data": data, "event": event}
        await self.channel_layer.group_send(self.channel, data)

    async def response_proxy(self, event):
        await self._send_message(event['data'], event=event.get('event'))

    async def _send_message(self, data, event=None):
        await self.send_json(content={
            "status": "ok",
            "data": data,
            "event": event
            })

    async def _throw_error(self, data, event=None):
        await self.send_json(content={
            "status": "error",
            "data": data,
            "event": event
            })

    async def connect(self):
        await self.accept()
        print(self.scope["user"])
        if "user" not in self.scope or self.scope["user"].is_anonymous:
            await self._send_message({"detail": "Authorization failed"})
            await self.close(code=1000)
            return

    async def receive_json(self, content, **kwargs):
        message = await self.parse_content(content)
        if message:
            event = message['event'].replace('.', '_')
            method = getattr(self, f"event_{event}", self.method_undefined) # функция getattr получает объект и старается получить метод f"event_{event}
            await method(message)
        else:
            await self._throw_error({"detail": "Invalid message"})


    async def method_undefined(self, message):
        await self._throw_error({'detail': 'Unknown event'}, event=message['event'])

    @classmethod
    async def parse_content(cls, content):
        if isinstance(content, dict) and isinstance(content.get("event"), str) and \
            isinstance(content.get("data"), dict):
            return content

    