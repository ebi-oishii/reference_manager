from django.urls import path

from . import views

app_name = "papers"

urlpatterns = [
    path('import_paper', views.import_paper, name="import_paper"),
    path('paper_list', views.paper_list, name="paper_list"),
    path('paper_detail/<uuid:paper_id>', views.paper_detail, name="paper_detail"),
#    path('detail/<uuid:pk>', views.project_detail, name="project_detail"),
#    path('add_post/<uuid:project_id>', views.create_post, name="create_post")
]