from django.contrib import admin
from django.urls import path
from map import views as app_views
from friends import views as friends_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # friends app views
    path('friendList/', friends_views.friendList, name='friendList'),
    path('sendFriendRequest/', friends_views.sendFriendRequest, name='sendFriendRequest'),
    path('acceptFriendRequest/<int:requestId>/', friends_views.acceptFriendRequest, name='acceptFriendRequest'),
    path('declineFriendRequest/<int:requestId>/', friends_views.declineFriendRequest, name='declineFriendRequest'),
    path('cancelFriendRequest/<int:requestId>/', friends_views.cancelFriendRequest, name='cancelFriendRequest'),
    path('removeFriend/<int:friendId>/', friends_views.removeFriend, name='removeFriend'),
    # map app views
    path('', app_views.map, name='home'),
    path('login/', app_views.user_login, name='login'),
    path('join/', app_views.join, name='join'),
    path('logout/', app_views.user_logout, name='logout'),
    path('map/', app_views.map, name='map'),
    path('gMap/', app_views.loadMapAPI, name='gMap'),
    path('setDistancePreference/', app_views.setDistancePreference, name='setDistancePreference'),
    path('setColorPreference/', app_views.setColorPreference, name='setColorPreference'),
    path('setIconPreference/', app_views.setIconPreference, name='setIconPreference'),
]