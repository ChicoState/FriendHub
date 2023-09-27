from django.db import models
from django.contrib.auth.models import User
# from django.contrib.postgres.fields import ArrayField



class UserData(models.Model):
    #store user in "user"
    user = models.ForeignKey(User, on_delete=models.CASCADE);
    #store location in "latitude" and "longitude"
    latitude = models.FloatField(default=0.00)
    longitude = models.FloatField(default=0.00)
    
    friends = models.ManyToManyField(User) # you can also define this relationship to MyUser


    def __str__(self) -> str:
        return self.username
    
