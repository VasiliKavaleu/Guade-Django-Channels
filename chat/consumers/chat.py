from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from chat.models import GroupParticipant, ChatGroup, ChatMessage
from .base import BaseChatConsumer


class ChatConsumer(BaseChatConsumer):
    """
        Connect to group: ws://127.0.0.1:8000/ws/chat/group_id/
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_id = None
        self.group = None
        self.participants = []
        self.channel = None                    

    async def connect(self):                                        # обрабатываем подключение
        await super().connect()
        self.group_id = self.scope['url_route']['kwargs']['group_id']            # получение id группы из websocket url
        self.channel = f"group_{self.group_id}"                     # идентификатор группы в формате в соответствии с channel_name из models

        group = await self.get_group()                              # получение группы с id = self.group_id из init
        if not group:                                               # проверка существует ли группа 
            await self._throw_error({'detail': 'Group not found'})  # если группы нету - посылаем сообщение с ошибкой
            await self.close()                                      # разрываем соединение
            return

        participants = await self.get_participants()                      # получение всех участников группы с id = self.group_id из init
        if self.scope['user'].id not in participants:               # проверка на вхождение у частника в группу
            await self._throw_error({'detail': 'Access denied'}) 
            await self.close()
            return

        # после проверки существования группы и вхождения пользователя в группу - добавляем соединеине пользователя в channel_layer redis
        await self.channel_layer.group_add(self.channel, self.channel_name) # self.channel_name - идентификатор соединения конкретного пользователя

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.channel, self.channel_name) # удаление пользователя из группы в channel_layer
        await super().disconnect(code)

    async def event_add_participant(self, event):
        """
            Add participant in current group: {"event":"add.participant","data":{"user_id":2}}
        """
        user_id = event['data'].get('user_id')
        if not user_id:
            return await self._throw_error({'detail': 'Missing user id'}, event['event'])
        await self.add_participant(user_id)
        participants = await self.get_participants()
        return await self._send_message(participants, event=event['event'])

    async def event_send_message(self, event):
        """
            Send message to current group: {"event":"send.message","data":{"message":"Good morning there"}}
        """
        message = event['data'].get('message')
        if not message:
            return await self._throw_error({'detail': 'Missing message'}, event['event'])
        await self.save_message(message, self.scope['user'])
        data = {
            'username': self.scope['user'].username,
            'message': event['data']['message'],
        }
        return await self._group_send(data, event=event['event'])

    async def event_list_messages(self, event):
        messages = await self.get_messages()
        return await self._send_message(messages, event=event['event'])
        

    @database_sync_to_async
    def get_group(self):
        group = ChatGroup.objects.filter(pk=self.group_id).first()
        if group:
            self.group = group
        return group

    @database_sync_to_async
    def get_participants(self):
        participants = list(GroupParticipant.objects.filter(group=self.group).values_list('user', flat=True))
        self.participants = participants
        return participants

    @database_sync_to_async
    def add_participant(self, user_id):
        user = get_user_model().objects.filter(pk=user_id).first()
        if user:
            participant, _ = GroupParticipant.objects.get_or_create(group=self.group, user=user)

    @database_sync_to_async
    def save_message(self, message, user):
        m = ChatMessage(message=message, group=self.group, user=user)
        m.save()

    @database_sync_to_async
    def get_messages(self):
        messages = ChatMessage.objects.select_related('user').filter(group=self.group).order_by('id')
        res = []
        for message in messages:
            res.append({
                'id': message.id,
                'username': message.user.username,
                'message': message.message,
            })
        return res