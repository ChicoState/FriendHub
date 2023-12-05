import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from friends.models import FriendList
from map.models import UserData
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async


class LocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.add_user_to_group()

    async def disconnect(self, close_code):
        pass

    @database_sync_to_async
    def get_user_data(self, username):
        user = User.objects.get(username=username)
        curUser = UserData.objects.get(djangoUser=user)
        friends = FriendList.objects.get(user=user)
        return curUser, friends

    @database_sync_to_async
    def update_user_data(self, curUser, lat, lng):
        curUser.latitude = lat
        curUser.longitude = lng
        curUser.save()
        return

    async def receive(self, text_data):
        # update user's location in the database
        content = json.loads(text_data)
        lat = content['lat']
        lng = content['lng']
        username = content['username']
        curUser, userFriends = await self.get_user_data(username)
        await self.update_user_data(curUser, lat, lng)
        # broadcast the new location to all friends
        async for friend in userFriends.friends.all():
            await self.channel_layer.group_send(
                f"user_{friend.username}",
                {
                    "type": "location_update",
                    "lat": lat,
                    "lng": lng,
                    "username": username,
                }
            )

    async def add_user_to_group(self):
        # get username from url
        user = self.scope['query_string'].decode('utf-8').split('=')[1]
        # add the user to a group based on their username
        await self.channel_layer.group_add(
            f"user_{user}",
            self.channel_name
        )

    async def location_update(self, event):
        lat = event['lat']
        lng = event['lng']
        username = event['username']
        message = {
            "type": "location_update",
            "lat": lat,
            "lng": lng,
            "username": username,
        }
        message_json = json.dumps(message)
        await self.send(message_json)