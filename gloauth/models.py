from django.db import models
from django.contrib.auth.models import User
from django.db.models import signals
import os
# Create your models here.
class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)
    user_profile_directory = '%s\\media\\' % os.getcwd()


    # Other fields here
    last_known_coordinates = models.CharField(max_length=100, default="uninitialized")
    user_profile_directory = '%s\\media\\' % os.getcwd()


    def __str__(self):
        return '%s' % self.user.username

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        user_profile_directory = '%s\\media\\' % os.getcwd()
        UserProfile.objects.create(user=instance)
        dirname = instance.username
        os.mkdir(os.path.join(user_profile_directory, dirname))


signals.post_save.connect(create_user_profile, sender=User)




class GloNote(models.Model):

    subject = models.CharField(max_length=100, unique=False)
    author = models.ForeignKey(User)
    textMessage = models.CharField(max_length=200, unique=False)
    coordinates = models.CharField(max_length=100, unique=False)
    image_filename = models.CharField(max_length=100, unique=False, null=True)
    def __str__(self):
        return '%s' % self.subject