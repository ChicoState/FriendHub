from django.db import models
from django.contrib.auth.models import User

class UserData(models.Model):
    #store user in "user"
    djangoUser = models.ForeignKey(User, on_delete=models.CASCADE)
    #store location in "latitude" and "longitude"
    latitude = models.FloatField(default=0.00)
    longitude = models.FloatField(default=0.00)

    friends = models.ManyToManyField('self', blank=True)

    
    def __str__(self) -> str:
        return self.djangoUser.username
    