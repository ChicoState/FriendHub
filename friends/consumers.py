import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        coordinates = json.loads(text_data)
        # Process the received coordinates as needed
        print(coordinates)
        # Send a confirmation message (optional tbh)
        await self.send(text_data=json.dumps({'message': 'Coordinates received successfully'}))