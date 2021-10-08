
ws://127.0.0.1:8000/ws/groups/

List all groups of current user
{"event":"group.list","data":{}}

List all users except current user
{"event":"user.list","data":{}}

Create a group and add current user in it
{"event":"group.create","data":{"name":"Name Group1"}}


ws://127.0.0.1:8000/ws/chat/group_id/