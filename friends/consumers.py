import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from friends.models import FriendList
from map.models import UserData
from django.contrib.auth.models import User
from channels.db import database_sync_to_async


class LocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    @database_sync_to_async
    def getUserData(self, username):
        user = User.objects.get(username=username)
        curUser = UserData.objects.get(djangoUser=user)
        friends = curUser.friends.all()
        return curUser, friends

    @database_sync_to_async
    def updateUserData(self, curUser, lat, lng):
        curUser.latitude = lat
        curUser.longitude = lng
        curUser.save()

    async def receive(self, text_data):
        # Update user's location in the database
        content = json.loads(text_data)
        lat = content['lat']
        lng = content['lng']
        username = content['username']
        curUser, friends = await self.getUserData(username)
        await self.updateUserData(curUser, lat, lng)

        # # Broadcast the new location to all friends
        # for friend in friends:
        #     await self.channel_layer.group_send(
        #         f"user_{friend.username}",
        #         {
        #             "type": "location.update",
        #             "lat": lat,
        #             "lng": lng,
        #             "username": username,
        #         }
        #     )

    # async def location_update(self, event):
    #     # Send the new location to the client
    #     await self.send_json(event)