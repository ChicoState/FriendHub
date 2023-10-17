from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from application.forms import JoinForm, LoginForm, DistancePreferenceForm, ColorPreferenceForm
from django.contrib.auth.decorators import login_required
from .models import UserData, FriendRequest, FriendList
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q

import requests
import os

# Your views go here


@login_required(login_url='/login/')
def home(request):
    return render(request, 'map.html')

@login_required(login_url='/login/')
def map(request):
    # get user data for current user
    userData = UserData.objects.get(djangoUser=request.user)
    currentDistancePreference = userData.distancePreference
  
    # get or create friendlist for the current user
    _, _ = FriendList.objects.get_or_create(user=request.user)
    # instantiate the distance preference form
    form = DistancePreferenceForm(initial={'distance': currentDistancePreference})

    # get the user's details
    latitude = userData.latitude
    longitude = userData.longitude

    # get the friend's details using the get_friends_coordinates function
    friends_details = userData.get_friends_coordinates()
    context = {
        'latitude': latitude,
        'longitude': longitude,
        'friends_details': friends_details,
        'form': form
    }
    return render(request, 'map.html', context)

def join(request):
    # if someone submitted a join form (created account)
    if (request.method == "POST"):
        jform = JoinForm(request.POST)
        # check if form is valid
        if (jform.is_valid()):
            # save form data to DB
            user = jform.save()
            # encrypt the password
            user.set_password(user.password)
            # save encrypted password to DB
            user.save()
            lat = jform.cleaned_data["lat"]
            lng = jform.cleaned_data["lng"]
            new_user = UserData.objects.create(
                djangoUser = user,
                latitude = lat,
                longitude = lng,
                distancePreference = 1
            )
            new_user.save()
            # success
            return redirect("/map")
        else:
            # invalid form
            page_data = { "join_form": jform }
            return render(request, 'join.html', page_data)
    else:
        # a get request, someone is trying to sign up so send them the join form
        jform = JoinForm()
        page_data = { "join_form": jform }
        return render(request, 'join.html', page_data)

def user_login(request):
    # if someone sent login form
    if (request.method == 'POST'):
        # create a LoginForm instance with sent data
        lform = LoginForm(request.POST)
        # check if form is valid
        if lform.is_valid():
            # extract the username and password from the form's cleaned data
            username = lform.cleaned_data["username"]
            password = lform.cleaned_data["password"]
            # authenticate the user
            user = authenticate(username=username, password=password)
            if user:
                # check if the user account is active
                if user.is_active:
                    # update to current lat/lng coords
                    lat = lform.cleaned_data["lat"]
                    lng = lform.cleaned_data["lng"]
                    userData = UserData.objects.get(djangoUser = user)
                    userData.latitude = lat
                    userData.longitude = lng
                    userData.save()
                    # log in the user and redirect to the home page
                    login(request, user)
                    return redirect("/map")
                else:
                    # return an HttpResponse indicating that the account is not active
                    return HttpResponse("This account is not active.")
            else:
                # if authentication fails, re-render the login form with an error message
                return render(request, 'login.html', {"login_form": LoginForm, "correct": False})
    else:
        # someone is trying to access the login form, so send the form
        return render(request, 'login.html', {"login_form": LoginForm, "correct": True})

@login_required(login_url='/login/')
def user_logout(request):
    logout(request)
    return redirect("/login/")

@login_required(login_url='/login/')
def loadMapAPI(request):
        API_KEY = os.getenv('API_KEY')
        url = f'https://maps.googleapis.com/maps/api/js?key={API_KEY}&callback=initMap'
        response = requests.get(url)
        return HttpResponse(response.content, content_type='application/javascript')

@login_required(login_url='/login/')
def friendList(request):
    # retrieve friend requests for the current user
    friendRequestsReceived = FriendRequest.objects.filter(receiver=request.user)
    friendRequestsSent = FriendRequest.objects.filter(sender=request.user)
    
    # get or create friendlist for the current user
    friends, _ = FriendList.objects.get_or_create(user=request.user)
    
    # get user data for current user
    userData = UserData.objects.get(djangoUser=request.user)
    currentDistancePreference = userData.distancePreference
    currentColorPreference = userData.colorPreference
    
    # instantiate the distance preference form
    form = DistancePreferenceForm(initial={'distance': currentDistancePreference})

    colorForm = ColorPreferenceForm(initial={'color': currentColorPreference})


    context = {
        'friendRequestsReceived': friendRequestsReceived,
        'friendRequestsSent': friendRequestsSent,
        'friends': friends.friends.all(),
        'form': form,
        'colorForm': colorForm
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
    
    try:
        # get the user instance for the friend to remove
        friendToRemove = User.objects.get(id=friendId)
        
        # remove the friend
        userFriendList = FriendList.objects.get(user=currentUser)
        userFriendList.unfriend(friendToRemove)
        messages.success(request, f"Successfully unfriended {friendToRemove.username}!")
        
        # remove any friend requests between the two users
        FriendRequest.objects.filter(
            Q(sender=currentUser, receiver=friendToRemove) | 
            Q(sender=friendToRemove, receiver=currentUser)
        ).delete()
    except User.DoesNotExist:
        messages.error(request, "User does not exist!")
    except FriendList.DoesNotExist:
        messages.error(request, "Friend list not found!")
    
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

@login_required(login_url='/login/')
def setDistancePreference(request):
    if request.method == 'POST':
        # handle post method for setting distance preference
        form = DistancePreferenceForm(request.POST)
        if form.is_valid():
            # update user's distance preference
            distanceSelected = form.cleaned_data.get('distance')
            userData = UserData.objects.get(djangoUser=request.user)
            userData.distancePreference = distanceSelected
            userData.save()
            return redirect('friendList')

    context = {'form': form}
    return render(request, 'friendList.html', context)

@login_required(login_url='/login')
def setColorPreference(request):
    if request.method == 'POST':
        # handle post method for setting color preference
        form = ColorPreferenceForm(request.POST)
        if form.is_valid():
            #update users color preference
            colorSelected = form.cleaned_data.get('color')
            userData = UserData.objects.get(djangoUser=request.user)
            userData.colorPreference = colorSelected
            userData.save()
            return redirect('friendList')
