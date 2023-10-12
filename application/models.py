from django.db import models
from django.contrib.auth.models import User
import random

class FriendList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'user')
    friends = models.ManyToManyField(User, blank=True, related_name='friends')

    def __str__(self):
        return self.user.username
    
    def addFriend(self, account):
        # Add a new friend
        if not account in self.friends.all():
            self.friends.add(account)
    
    def removeFriend(self, account):
        # Remove a friend
        if account in self.friends.all():
            self.friends.remove(account)
    
    def unfriend(self, removee):
        # Initiate unfriending someone :(
        removerFriendsList = self # person removing the other person
        removerFriendsList.removeFriend(removee)
        # Removing user from removee friend list
        friendList = FriendList.objects.get(user=removee)
        friendList.removeFriend(self.user)

    def isMutualFriend(self, friend):
        if friend in self.friends.all():
            return True
        return False

class FriendRequest(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')

    class Meta:
        unique_together = [['sender', 'receiver']]

    def __str__(self):
        return self.sender.username
    
    def accept(self):
        receiverFriendList = FriendList.objects.get(user=self.receiver)
        if receiverFriendList:
            receiverFriendList.addFriend(self.sender)
            senderFriendList = FriendList.objects.get(user=self.sender)
            if senderFriendList:
                senderFriendList.addFriend(self.receiver)
                self.delete()  # Delete the friend request after accepting
    
    def decline(self):
        self.delete()  # Delete the friend request after declining
    
    def cancel(self):
        self.delete()  # Delete the friend request after canceling

class UserData(models.Model):
    #store user in "user"
    djangoUser = models.ForeignKey(User, on_delete=models.CASCADE)
    #store location in "latitude" and "longitude"
    latitude = models.FloatField(default=0.00)
    longitude = models.FloatField(default=0.00)
    distancePreference = models.IntegerField(default=1)
    colorPreference = models.IntegerField(default=1)
    friends = models.ManyToManyField('self', blank=True)

    def __str__(self) -> str:
        return self.djangoUser.username
    
    def get_obfuscated_location(self):
        # map distance preferences to radius in meters
        preference_to_radius = {
            1: 0, 
            2: 500,    
            3: 1000,   
            4: 2500,   
            5: 5000,   
        }

        radius_in_meters = preference_to_radius.get(self.distancePreference, 100)  # default is 100m
        radius_in_degrees = radius_in_meters / 111320  # approximate conversion from meters to degrees

        # If the preference is for the exact location, return the actual coordinates
        if radius_in_meters == 0:
            return self.latitude, self.longitude

        # calculate a random offset, but ensure it's no more than one-quarter of the radius.
        # this ensures that the user's location is still within the circle.
        max_offset = radius_in_degrees / 4
        offset_lat = random.uniform(-max_offset, max_offset)
        offset_lng = random.uniform(-max_offset, max_offset)

        # Calculate the new obfuscated coordinates
        new_latitude = self.latitude + offset_lat
        new_longitude = self.longitude + offset_lng

        # Ensure the new coordinates are within valid range
        new_latitude = max(min(new_latitude, 90), -90)
        new_longitude = max(min(new_longitude, 180), -180)

        return new_latitude, new_longitude


    def get_friends_coordinates(self):
        # get the FriendList instance for this user
        friend_list_instance = FriendList.objects.get(user=self.djangoUser)

        # initialize an empty list to store friends' coordinates
        coords_list = []

        # iterate over the friends and fetch their coordinates from the UserData model
        for friend in friend_list_instance.friends.all():
            user_data_instance = UserData.objects.get(djangoUser=friend)
            obfuscated_latitude, obfuscated_longitude = user_data_instance.get_obfuscated_location()

            coords = {
                'username': friend.username,
                'latitude': obfuscated_latitude,
                'longitude': obfuscated_longitude,
                'distancePreference': user_data_instance.distancePreference,
                'color': user_data_instance.colorPreference
            }
            coords_list.append(coords)

        return coords_list

    