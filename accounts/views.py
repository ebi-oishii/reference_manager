from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views import View
from django.contrib.auth import login, authenticate
from django.urls import reverse, reverse_lazy

from django.views.generic import TemplateView, DetailView, CreateView
from django.contrib.auth import views as auth_views

from .forms import RegisterForm
import base58
from .models import CustomUser, Collaboration

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
    next_page = "accounts:login"

logout = LogoutView.as_view()


class RegisterView(CreateView):
    model = CustomUser
    template_name = 'accounts/register.html'
    form_class = RegisterForm

    def get_success_url(self):
        return reverse_lazy("accounts:profile", kwargs={"profile_username": self.object.username})
    
    def form_valid(self, form):
        user = form.save(commit=False)
        
        # パスワードをハッシュ化して保存
        user.set_password(form.cleaned_data["password"])  # ハッシュ化
        user.save()  # ユーザーをデータベースに保存

        # 認証後にログイン
        auth_user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
        login(self.request, auth_user)
        return super().form_valid(form)

register = RegisterView.as_view()


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


class SendCollaborationRequestView(View):
    def get(self, request, username):
        to_user = get_object_or_404(CustomUser, username=username)

        existing_request = Collaboration.objects.filter(from_user=request.user, to_user=to_user).first()
        if existing_request:
            if existing_request.status == "accepted":
                return redirect("accounts:profile", kwargs={"username": request.user.username})
            else:
                return redirect("accounts:profile", kwargs={"username": request.user.username})
            
        Collaboration.objects.create(from_user=request.user, to_user=to_user, status="pending")
        return redirect("accounts:profile", kwargs={"username": request.user.username})

send_collaboration_request = SendCollaborationRequestView.as_view()
