from django.contrib import admin
from django.urls import path
from application import views as app_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("friendList/", app_views.friendList, name='friendList'),
    path("", app_views.map),
    path("login/", app_views.user_login),
    path("join/", app_views.join),
    path("logout/", app_views.user_logout),
    path("map/", app_views.map),
    path('gMap/', app_views.loadMapAPI, name='gMap'),
    path('sendFriendRequest/', app_views.sendFriendRequest, name='sendFriendRequest'),
    path('acceptFriendRequest/<int:requestId>/', app_views.acceptFriendRequest, name='acceptFriendRequest'),
    path('declineFriendRequest/<int:requestId>/', app_views.declineFriendRequest, name='declineFriendRequest'),
    path('cancelFriendRequest/<int:requestId>/', app_views.cancelFriendRequest, name='cancelFriendRequest'),
    path('removeFriend/<int:friendId>/', app_views.removeFriend, name='removeFriend'),
    path('setDistancePreference/', app_views.setDistancePreference, name='setDistancePreference'),
]