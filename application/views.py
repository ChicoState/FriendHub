import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from application.forms import JoinForm, LoginForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import UserData
from django.http import JsonResponse
from django.core import serializers




import requests
import os

#models
from application.models import UserData

@login_required(login_url='/login/')
def home(request):
    return render(request, 'home.html')

@login_required(login_url='/login/')
def friendList(request):
    return render(request, 'friendList.html')

@login_required(login_url='/login/')
def map(request):
    user_data = UserData.objects.get(djangoUser=request.user)

    username = user_data.djangoUser.username
    firstname = user_data.djangoUser.first_name
    latitude = user_data.latitude
    longitude = user_data.longitude

    friends = user_data.friends.all()

    friends_first_name = [friend.djangoUser.user.name for friend in friends]
    friends_lat = [friend.latitude for friend in friends]
    friends_long = [friend.longitude for friend in friends]

    context = {
        'username': username,
        'firstname': firstname,
        'latitude': latitude,
        'longitude': longitude,
        'friends_first_name': friends_first_name,
        'friends_lat': friends_lat,
        'friends_long': friends_long,
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
                 longitude = lng
            )
            new_user.save()
            # success
            return redirect("/")
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
                    # log in the user and redirect to the home page
                    login(request, user)
                    return redirect("/")
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
    return redirect("/")

@login_required(login_url='/login/')
def loadMapAPI(request):
        API_KEY = os.getenv('API_KEY')
        url = f'https://maps.googleapis.com/maps/api/js?key={API_KEY}&callback=initMap'
        response = requests.get(url)
        return HttpResponse(response.content, content_type='application/javascript')



def populate_all_users(request):
    # Fetch data from the Friend model
    all_users = UserData.objects.values('id', 'djangoUser__username', 'latitude', 'longitude')

    all_users_json = json.dumps(list(all_users))
    
    # Pass the data to the template
    # return render(request, 'friendList.html', {'all_users': all_users})

    return JsonResponse({'all_users': all_users_json})


@login_required
def add_friend(request):
    if request.method == 'POST':
        friend_username = request.POST.get('username')
        print(f"Friend username from POST: {friend_username}")  # Debug statement

        try:
            friend_user_data = UserData.objects.get(djangoUser__username=friend_username)
            print(f"Found friend_user_data: {friend_user_data}")  # Debug statement

            user_data = UserData.objects.get(djangoUser=request.user)
            print(f"User data for the logged-in user: {user_data}")  # Debug statement

            # Check if the friend is not already in the user's friend list
            if friend_user_data != user_data and not user_data.friends.filter(djangoUser=friend_user_data.djangoUser).exists():
                user_data.friends.add(friend_user_data.djangoUser)
                user_data.save()
                return JsonResponse({'success': True, 'message': 'Friend added successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'Friend is already in your friend list or is yourself.'})
        except UserData.DoesNotExist:
            print(f"User with username '{friend_username}' does not exist.")  # Debug statement
            return JsonResponse({'success': False, 'message': 'User with that username does not exist.'})
    else:
        print("Invalid request method.")  # Debug statement
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})


