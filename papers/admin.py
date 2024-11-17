from django.contrib import admin
from .models import Paper, Author, Publisher, University
# Register your models here.

admin.site.register(Paper)
admin.site.register(Author)
admin.site.register(Publisher)
admin.site.register(University)