"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import TemplateView
# from accounts import views as accounts_views
# from papers import views as papers_views
# from research_projects import views as research_project_views
#from . import views

class TopPageView(TemplateView):
    template_name = "index.html"

top_page = TopPageView.as_view()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', top_page, name="top_page"),
    path('accounts/', include('accounts.urls')),
    path('papers/', include('papers.urls')),
    path('research_projects/', include('research_projects.urls'))
    
]
