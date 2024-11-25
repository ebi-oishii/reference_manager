from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path('', views.index, name="index"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('register/', views.register, name="register"),
    path('user/<str:profile_username>/', views.profile, name="profile"),
    path('collaboration/request/<uuid:to_user_id>/', views.send_collaboration_request, name="send_collaboration_request"),
    path('collaboration/respond/<uuid:request_id>/<str:response>', views.manage_collaboration_request, name="manage_collaboration_request"),
    path('collaboration/withdraw/<uuid:request_id>/', views.withdraw_collaboration_request, name="withdraw_collaboration_request"),
    path('user_search', views.user_search, name="user_search"),
    path('collaboration/list/<str:username>', views.collaboration_request_list, name="collaboration_request_list"),
]