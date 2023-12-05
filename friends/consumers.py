import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

class LocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        #self.user = self.scope["user"]
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive_json(self, content):
        # Update user's location in the database
        lat = content['lat']
        lng = content['lng']
        username = content['username']

        friend = FriendList.objects.get(user=username)

        user = UserData.objects.get(djangoUser=username)  
        user.latitude = lat
        user.longitude = lng
        user.save()

        # Broadcast the new location to all friends
        friends = user.friends.all()
        for friend in friends:
            await self.channel_layer.group_send(
                f"user_{friend.username}",
                {
                    "type": "location.update",
                    "lat": lat,
                    "lng": lng,
                    "username": username,
                }
            )

    # async def location_update(self, event):
    #     # Send the new location to the client
    #     await self.send_json(event)

# import json
# from channels.generic.websocket import AsyncWebsocketConsumer

# class LocationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()

#     async def disconnect(self, close_code):
#         pass

#     async def receive(self, text_data):
#         coordinates = json.loads(text_data)
#         # Process the received coordinates as needed
#         print(coordinates)
#         # Send a confirmation message (optional tbh)
#         await self.send(text_data=json.dumps({'message': 'Coordinates received successfully'}))