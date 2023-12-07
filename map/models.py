from django.db import models
from django.contrib.auth.models import User
import random
from friends.models import FriendList

# model to store the preference's friends have 4 u
class FriendLocationPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="location_preferences")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_preferences")
    distancePreference = models.IntegerField(default=6)

    class Meta:
        unique_together = ('user', 'friend')

# user data, self explanatory
class UserData(models.Model):
    djangoUser = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.FloatField(default=0.00)
    longitude = models.FloatField(default=0.00)
    colorPreference = models.CharField(default = "#0035fe", max_length=7)
    iconPreference = models.IntegerField(default=1)
    friends = models.ManyToManyField('self', blank=True)
    
    def get_obfuscated_location_for_friend(self, friend_user):
        try:
            preference = FriendLocationPreference.objects.get(user=self.djangoUser, friend=friend_user).distancePreference
        except FriendLocationPreference.DoesNotExist:
            preference = 6

        # if the preference is for the exact location or hiding it, return the actual or zero coordinates
        if preference == 1:
            return self.latitude, self.longitude
        elif preference == 6:
            return 0, 0

        # map distance preferences to radius in meters
        preference_to_radius = {
            2: 500,
            3: 1000,
            4: 2500,
            5: 5000,
        }

        radius_in_meters = preference_to_radius.get(preference, 500)
        # approximate conversion from meters to degree
        radius_in_degrees = radius_in_meters / 111320 

        # calculate a random offset within the radius
        max_offset = radius_in_degrees / 2 
        offset_lat = random.uniform(-max_offset, max_offset)
        offset_lng = random.uniform(-max_offset, max_offset)

        # calculate new obfuscated coordinates
        new_latitude = self.latitude + offset_lat
        new_longitude = self.longitude + offset_lng

        # ensure coordinates are within valid range
        new_latitude = max(min(new_latitude, 90), -90)
        new_longitude = max(min(new_longitude, 180), -180)

        return new_latitude, new_longitude


    def get_friends_coordinates(self):
        friend_list_instance = FriendList.objects.get(user=self.djangoUser)
        coords_list = []

        for friend in friend_list_instance.friends.all():
            friend_user_data = UserData.objects.get(djangoUser=friend)

            # fetch the obfuscated location for the friend from the perspective of the current user
            obfuscated_latitude, obfuscated_longitude = friend_user_data.get_obfuscated_location_for_friend(self.djangoUser)

            # fetch the friend's distance preference for the current user
            distance_preference = FriendLocationPreference.objects.filter(user=friend, friend=self.djangoUser).first()
            distance_preference_value = distance_preference.distancePreference if distance_preference else 6

            coords = {
                'username': friend.username,
                'latitude': obfuscated_latitude,
                'longitude': obfuscated_longitude,
                'distancePreference': distance_preference_value,
                'color': friend_user_data.colorPreference,
                'icon': friend_user_data.iconPreference
            }
            coords_list.append(coords)

        return coords_list

    