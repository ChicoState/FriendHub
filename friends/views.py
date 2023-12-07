from django.shortcuts import render, redirect, get_object_or_404
from map.forms import DistancePreferenceForm, ColorPreferenceForm, IconPreferenceForm
from django.contrib.auth.decorators import login_required
from map.models import UserData, FriendLocationPreference
from .models import FriendRequest, FriendList
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q

@login_required(login_url='/login/')
def friendList(request):
    # retrieve friend requests for the current user
    friendRequestsReceived = FriendRequest.objects.filter(receiver=request.user)
    friendRequestsSent = FriendRequest.objects.filter(sender=request.user)
    
    # get or create friendlist for the current user
    friends, _ = FriendList.objects.get_or_create(user=request.user)
    
    # get user data for current user
    userData = UserData.objects.get(djangoUser=request.user)
    currentColorPreference = userData.colorPreference
    currentIconPreference = userData.iconPreference

    # create a dictionary to hold a form for each friend
    friend_forms = {}
    for friend in friends.friends.all():
        # get the current distance preference for the friend
        preference, _ = FriendLocationPreference.objects.get_or_create(user=request.user, friend=friend, defaults={'distancePreference': 6})
        friend_forms[friend] = DistancePreferenceForm(initial={'friend_id': friend.id, 'distance': preference.distancePreference})
    colorForm = ColorPreferenceForm(initial={'color': currentColorPreference})
    iconForm = IconPreferenceForm(initial={'icon': currentIconPreference})

    context = {
        'friendRequestsReceived': friendRequestsReceived,
        'friendRequestsSent': friendRequestsSent,
        'friend_forms': friend_forms,
        'colorForm': colorForm,
        'iconForm': iconForm,
        'pfpNum': currentIconPreference,
    }
    
    return render(request, 'friendList.html', context)

@login_required(login_url='/login/')
def sendFriendRequest(request):
    if request.method == 'POST':
        # get the username from the post data
        username = request.POST.get('username1')
        try:
            # get the user instance for the provided username
            receiver = User.objects.get(username=username)
            # check if self-friend request
            if receiver.username != request.user.username:
                # check for mutual friendship
                senderFriendList = FriendList.objects.get(user=request.user)
                if senderFriendList.isMutualFriend(receiver):
                    messages.warning(request, "You are already friends!")
                    return redirect('friendList')
                # check for existing friend request
                existingRequest = FriendRequest.objects.filter(sender=request.user, receiver=receiver).exists()
                if not existingRequest:
                    # check if there's a pending friend request from the receiver
                    pendingRequestFromReceiver = FriendRequest.objects.filter(sender=receiver, receiver=request.user).exists()
                    if not pendingRequestFromReceiver:
                        FriendRequest.objects.create(sender=request.user, receiver=receiver)
                        messages.success(request, "Friend request sent!")
                    else:
                        messages.warning(request, "You already have a pending friend request from this user!")
                else:
                    messages.warning(request, "Friend request already sent!")
            else:
                messages.warning(request, "You cannot send a friend request to yourself!")
        except User.DoesNotExist:
            messages.error(request, "User does not exist!")
    return redirect('friendList')

@login_required(login_url='/login/')
def removeFriend(request, friendId):
    # get the current user
    currentUser = request.user
    # get the user instance for the friend to remove
    friendToRemove = User.objects.get(id=friendId)
        
    # remove the friend
    userFriendList = FriendList.objects.get(user=currentUser)
    userFriendList.unfriend(friendToRemove)
    messages.success(request, f"Successfully unfriended {friendToRemove.username}!")
        
    # remove any friend requests between the two users how does this shit work???!????
    FriendRequest.objects.filter(
        Q(sender=currentUser, receiver=friendToRemove) | 
        Q(sender=friendToRemove, receiver=currentUser)
    ).delete()
    
    return redirect('friendList')

@login_required(login_url='/login/')
def acceptFriendRequest(request, requestId):  
    # get the friend request object
    friendRequest = get_object_or_404(FriendRequest, id=requestId, receiver=request.user)
    
    # accept the friend request
    friendRequest.accept()
    return redirect('friendList')

@login_required(login_url='/login/')
def declineFriendRequest(request, requestId):
    # get the friend request object
    friendRequest = get_object_or_404(FriendRequest, id=requestId, receiver=request.user)
    
    # decline the friend request
    friendRequest.decline()
    return redirect('friendList')

@login_required(login_url='/login/')
def cancelFriendRequest(request, requestId):
    # get the friend request object
    friendRequest = get_object_or_404(FriendRequest, id=requestId, sender=request.user)
    
    # cancel the friend request
    friendRequest.cancel()
    return redirect('friendList')