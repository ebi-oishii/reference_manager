from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.http import JsonResponse
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
    def post(self, request, *args, **kwargs):
        to_user = get_object_or_404(CustomUser, user_id=kwargs["to_user_id"])

        collaboration, created = Collaboration.objects.get_or_create(from_user=request.user , to_user=to_user)
        if created:
            return JsonResponse({"message": "既に送信されています"})
        else:
            return JsonResponse({"message": "送信されました"})

send_collaboration_request = SendCollaborationRequestView.as_view()


class ManageCollaborationRequestView(View):
    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        collaboration_request = get_object_or_404(Collaboration, request_id=kwargs.get("request_id"))
        
        if action == "accept":
            collaboration_request.status = "accepted"
            collaboration_request.save()
            return JsonResponse({"message": "request accepted"})
        
        elif action == "reject":
            collaboration_request.delete()
            return JsonResponse({"message": "request rejected"})
        
        else:
            return JsonResponse({"message": "invalid response"})
        
manage_collaboration_request = ManageCollaborationRequestView.as_view()

            