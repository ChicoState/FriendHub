from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from map.forms import JoinForm, LoginForm, DistancePreferenceForm, ColorPreferenceForm, IconPreferenceForm
from django.contrib.auth.decorators import login_required
from .models import UserData, FriendLocationPreference
from friends.models import FriendRequest, FriendList
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q


import requests
import os
import json

@login_required(login_url='/login/')
def home(request):
    return render(request, 'map.html')

@login_required(login_url='/login/')
def map(request):
    # get user data for current user
    userData = UserData.objects.get(djangoUser=request.user)  
    # get or create friendlist for the current user
    _, _ = FriendList.objects.get_or_create(user=request.user)

    # get the user's details
    latitude = userData.latitude
    longitude = userData.longitude

    # get the friend's details using the get_friends_coordinates function
    friends_details = userData.get_friends_coordinates()
    # get pfp json
    with open('./static/json/pfps.json', 'r') as file:
        pfps_data = json.load(file)

    context = {
        'latitude': latitude,
        'longitude': longitude,
        'friends_details': friends_details,
        'pfps_json': pfps_data,
        'username': request.user
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
def setDistancePreference(request):
    if request.method == 'POST':
        form = DistancePreferenceForm(request.POST)
        if form.is_valid():
            friend_id = form.cleaned_data.get('friend_id')
            distanceSelected = form.cleaned_data.get('distance')
            print(distanceSelected)
            # Fetch the friend user instance
            friend_user = get_object_or_404(User, pk=friend_id)
            # Update or create the FriendLocationPreference
            FriendLocationPreference.objects.update_or_create(
                user=request.user,
                friend=friend_user,
                defaults={'distancePreference': distanceSelected}
            )
            return redirect('friendList')
    return redirect('friendList')

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
        
    context = {'form': form}
    return render(request, 'friendList.html', context)

@login_required(login_url='/login')
def setIconPreference(request):
    if request.method == 'POST':
        # handle post method for setting icon preference
        form = IconPreferenceForm(request.POST)
        if form.is_valid():
            #update users icon preference
            iconSelected = form.cleaned_data.get('icon')
            userData = UserData.objects.get(djangoUser=request.user)
            userData.iconPreference = iconSelected
            userData.save()
            return redirect('friendList')
        
    context = {'form': form}
    return render(request, 'friendList.html', context)
