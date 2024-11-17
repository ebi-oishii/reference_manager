from django.contrib import admin
from .models import Project, Post, PapersIndices
# Register your models here.

admin.site.register(Project)
admin.site.register(Post)
admin.site.register(PapersIndices)