from django.contrib import admin
from .models import CustomUser, Collaboration

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Collaboration)