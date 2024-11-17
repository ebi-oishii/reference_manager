from django.urls import path

from . import views

app_name = "research_projects"

urlpatterns = [
    path('create_project/', views.create_project, name="create_project"),
    path('detail/<uuid:project_id>/', views.project_detail, name="project_detail"),
    path('add_post/<uuid:project_id>/', views.add_post, name="create_post"),
    path('add_paper/<uuid:project_id>/', views.add_paper, name="add_paper"),
    path('edit_citation/<uuid:project_id>/<int:index>', views.edit_citation, name="edit_citation"),
]