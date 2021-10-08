from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from chat.models import GroupParticipant, ChatGroup
from .base import BaseChatConsumer


class GroupChatConsumer(BaseChatConsumer):
    """
    Connect to: ws://127.0.0.1:8000/ws/groups/
    """
    async def event_group_list(self, event):
        """
        List all groups of current user
        {"event":"group.list","data":{}}
        """
        data = await self.group_list(self.scope["user"])
        await self._send_message(data, event=event['event'])

    async def event_user_list(self, event):
        """
        List all users except current user
        {"event":"user.list","data":{}}
        """
        data = await self.user_list(self.scope["user"])
        await self._send_message(data, event=event['event'])

    async def event_group_create(self, event):
        """
        Create a group and add current user in it
        {"event":"group.create","data":{"name":"Name Group1"}}
        """
        name = event['data'].get('name')
        if not name:
            return await self._throw_error({'detail': 'Missing group name'}, event=event['event'])
        data = await self.group_create(name, self.scope["user"])
        await self._send_message(data, event=event['event'])

    @database_sync_to_async
    def group_list(self, user):
        group_ids = list(GroupParticipant.objects.filter(user=user).values_list('group', flat=True))
        res = []
        # ChatGroup.objects.filter(group_participant__user=user) # альтернативный способ
        for g in ChatGroup.objects.filter(id__in=group_ids):
            res.append({
                "id": g.id,
                "name": g.name,
                "link": g.link,
            })
        return res

    @database_sync_to_async
    def user_list(self, user):
        users = get_user_model().objects.all().exclude(pk=user.id)
        res = []
        for u in users:
            res.append({
                "id": u.id,
                "username": u.username,
                "email": u.email
            })
            return res

    @database_sync_to_async
    def group_create(self, name, user):
        group = ChatGroup(name=name)
        group.save()
        participant = GroupParticipant(user=user, group=group)
        participant.save()
        return {"id": group.id, "name": group.name, "link": group.link}
