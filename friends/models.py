from django.db import models
from django.contrib.auth.models import User

class FriendList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'user')
    friends = models.ManyToManyField(User, blank=True, related_name='friends')

    def __str__(self):
        return self.user.username
    
    def addFriend(self, account):
        # add a new friend
        if not account in self.friends.all():
            self.friends.add(account)
    
    def removeFriend(self, account):
        # remove a friend
        if account in self.friends.all():
            self.friends.remove(account)
    
    def unfriend(self, removee):
        # initiate unfriending someone :(
        removerFriendsList = self # person removing the other person
        removerFriendsList.removeFriend(removee)
        # removing user from removee friend list
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
    # i mean just read the function name
    def accept(self):
        receiverFriendList = FriendList.objects.get(user=self.receiver)
        if receiverFriendList:
            receiverFriendList.addFriend(self.sender)
            senderFriendList = FriendList.objects.get(user=self.sender)
            if senderFriendList:
                senderFriendList.addFriend(self.receiver)
                self.delete()
    # deleting friend req after declining
    def decline(self):
        self.delete()
    # deleting friend req after cancelling
    def cancel(self):
        self.delete()
