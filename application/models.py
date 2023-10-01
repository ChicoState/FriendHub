from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
    
    def __str__(self) -> str:
        return self.djangoUser.username
    
    def get_friends_coordinates(self):
        
        # Get the FriendList instance for this user
        friend_list_instance = FriendList.objects.get(user=self.djangoUser)
        
        # Initialize an empty list to store friends' coordinates
        coords_list = []
        
        # Iterate over the friends and fetch their coordinates from the UserData model
        for friend in friend_list_instance.friends.all():
            user_data_instance = UserData.objects.get(djangoUser=friend)
            coords = {
                'username': friend.username,
                'latitude': user_data_instance.latitude,
                'longitude': user_data_instance.longitude
            }
            coords_list.append(coords)

        return coords_list

    