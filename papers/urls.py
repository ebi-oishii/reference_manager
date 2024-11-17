from django.urls import path

from . import views

app_name = "papers"

urlpatterns = [
    path('import_paper', views.import_paper, name="import_paper"),
#    path('detail/<uuid:pk>', views.project_detail, name="project_detail"),
#    path('add_post/<uuid:project_id>', views.create_post, name="create_post")
]