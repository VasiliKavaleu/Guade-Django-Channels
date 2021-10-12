## Example of using Django Channels via chat

Clone project 

Create virtual environment
```bash
python3 -m venv env
```

Activate virtual environment
```bash
source env/bin/activate
```

Install dependencies
```bash
pip install -r requirements.txt
```

Make migrations/migrate
```bash
python manage.py makemigrations
python manage.py migrate
```

Run Redis in container
```bash
docker-compose -f docker-compose.redis.yml up
```

Run server and leave comment under post (login is required)
```bash
python3 manage.py runserver
```
Go to the main main page (login required):
[chat](http://127.0.0.1:8000/)

Connect to:
```
ws://127.0.0.1:8000/ws/groups/
```
And send messages

List all groups of current user:
```
{"event":"group.list","data":{}}
```

List all users except current user:
```
{"event":"user.list","data":{}}
```

Create a group and add current user in it:
```
{"event":"group.create","data":{"name":"Name Group1"}}
```

Disconnect

Connect to:
```
ws://127.0.0.1:8000/ws/chat/group_id/
```
And send messages

Send message to group/chat:
```
{"event":"send.message","data":{"message":"5656"}}
```

Add participant in current chat/group: 
```
{"event":"add.participant","data":{"user_id":2}}
```
