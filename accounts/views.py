from django.shortcuts import render, get_object_or_404
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views import View
from django.contrib.auth import login as auth_login
from django.urls import reverse, reverse_lazy

from django.views.generic import TemplateView, DetailView
from django.contrib.auth import views as auth_views

#from .forms import LoginForm
import base58
from .models import CustomUser
# Create your views here.


class IndexView(TemplateView):
    template_name = "accounts/index.html"
    
index = IndexView.as_view()


class LoginView(auth_views.LoginView):
#    form_class = LoginForm
#デフォルトのAuthenticationFormを呼んでいる
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        username = self.request.user.username
        #ここでの"profile"はurl_patternsのnameに対応してる
        return reverse_lazy("accounts:profile", kwargs={"profile_username": username})
    
login = LoginView.as_view()


class LogoutView(auth_views.LogoutView):
    next_page = "/accounts/"

logout = LogoutView.as_view()


class ProfileView(DetailView):
    model = CustomUser
    template_name = 'accounts/profile.html'
    context_object_name = 'user'

    def get_object(self):
        """ユーザー名に基づいてプロフィールを取得"""
        username = self.kwargs.get('profile_username')
        user = get_object_or_404(CustomUser, username=username)
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ログインユーザーが自分のプロフィールページを表示しているか判定
        #self.objectはget_objectを通じて決定されます
        context['is_self'] = (self.request.user == self.object)
        context['user'] = self.request.user
        context['profile_user'] = self.object    
        context['profile_user_projects'] = self.object.projects.all()
        return context
    
profile = ProfileView.as_view()