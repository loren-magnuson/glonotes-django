from django.contrib import admin

# Register your models here.
from gloauth.models import UserProfile, GloNote
admin.site.register(UserProfile)
admin.site.register(GloNote)