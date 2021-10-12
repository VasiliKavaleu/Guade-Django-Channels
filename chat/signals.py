from django.db.models.signals import post_save
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer # позволяет получить CHANNEL_LAEYRS из settings

from .models import GroupParticipant, ChatMessage, ChatGroup


def send_chat_message(data, channel_name):
    async_to_sync(get_channel_layer().group_send)(channel_name, data)

def new_group(sender, instance, created, **kwargs):
    if created:
        # проверка не является ли создатель группы первым пользователем, т.к. нет необходимости уведомлять его о добавлении самого себя в группу
        first_participant = GroupParticipant.objects.filter(group=instance.group).order_by('-id').first()
        if first_participant.user.id != instance.user.id:
            data = {
                "type": "send.notice", # название метода который будет полусать из channel_layers данные и отправлять пользователю
                "data": {
                    "event": "new.group",
                    "data": {
                        "id": instance.group.id,
                        "name": instance.group.name,
                        "link": instance.group.link,
                    }
                }
            }

            channel_name = ChatGroup.user_channel_name(instance.user.id) # имя канала в который необходимо отправить данные - data
            send_chat_message(data, channel_name) # отправка сообщения когда в группу добавлен пользователь

def new_message(sender, instance, created, **kwargs):
    if created:
        data = {
            "type": "send.notice", 
            "data": {
                "event": "new.message",
                "data": {
                    "id": instance.id,
                    "group_id": instance.group.id,
                    "name": instance.group.name,
                    "message": instance.message,
                }
            }
        }
        participants = GroupParticipant.objects.filter(group=instance.group).exclude(user=instance.user)
        for participant in participants: # отправка уведомлений всем кто в группе
            channel_name = ChatGroup.user_channel_name(participant.user.id) 
            send_chat_message(data, channel_name) 

post_save.connect(new_group, sender=GroupParticipant, dispatch_uid='new_group_participant') 

post_save.connect(new_message, sender=ChatMessage, dispatch_uid='new_group_message') 
