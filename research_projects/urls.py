from django.urls import path

from . import views

app_name = "research_projects"

urlpatterns = [
    path('create_project/', views.create_project, name="create_project"),
    path('detail/<uuid:project_id>/', views.project_detail, name="project_detail"),
    path('add_post/<uuid:project_id>/', views.add_post, name="create_post"),
    path('search_paper/<uuid:project_id>/', views.search_paper, name="search_paper"),
    path('add_paper/<uuid:project_id>/<uuid:paper_id>/', views.add_paper, name="add_paper"),
    path('edit_citation/<uuid:project_id>/<int:index>', views.edit_citation, name="edit_citation"),
    path('project_list/', views.project_list, name="project_list"),
    path('add_member/<uuid:project_id>/', views.add_member, name="add_member"),
    path('public_switch/<uuid:project_id>/', views.public_switch, name="public_switch"),
    path('visible_switch/<uuid:project_id>/', views.visible_switch, name="visible_switch"),
]