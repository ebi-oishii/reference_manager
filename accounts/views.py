from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView
from django.contrib.auth import login, authenticate
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.views.generic import TemplateView, DetailView, CreateView, DeleteView
from django.contrib.auth import views as auth_views

from django.db.models import Q

from .forms import RegisterForm, UserSearchForm, ManageCollaborationRequestForm
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
        collaborators = Collaboration.objects.filter((Q(from_user=self.request.user) | Q(to_user=self.request.user)), status="accepted").values_list("from_user", "to_user")
        context['collaborator_list'] = [user   for pair in collaborators    for user in pair    if user != self.request.user.user_id]
        to_pending_collaborators = Collaboration.objects.filter(from_user=self.request.user, status="pending").values_list("to_user", flat=True)
        context['to_pending_collaborator_list'] = to_pending_collaborators
        from_pending_collaborators = Collaboration.objects.filter(to_user=self.request.user, status="pending").values_list("from_user", flat=True)
        context['from_pending_collaborator_list'] = from_pending_collaborators
        context['numbers'] = [1, 2, 3, 4] 
        if context["is_self"]:
            paginator = Paginator(self.object.projects.all().order_by("-updated_at"), 20)
        else:
            paginator = Paginator(self.object.projects.filter(Q(is_public=True) | Q(members=self.request.user)).order_by("-updated_at"), 20)

        page = self.request.GET.get("page")
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        context["page_obj"] = page_obj
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


class WithdrawCollaborationRequestView(View):
    def post(self, request, *args, **kwargs):
        collaboration_request = get_object_or_404(Collaboration, request_id=kwargs.get("request_id"))

        collaboration_request.delete()
        return JsonResponse({"message": "Withdrawed request"})

withdraw_collaboration_request = WithdrawCollaborationRequestView.as_view()


class ManageCollaborationRequestView(View):
    def post(self, request, *args, **kwargs):
        collaboration_request = get_object_or_404(Collaboration, request_id=kwargs.get("request_id"))
        
        if kwargs.get("response") == "accept":
            collaboration_request.status = "accepted"
            collaboration_request.save()
            return JsonResponse({"message": "request accepted"})
        
        elif kwargs.get("response") == "reject":
            collaboration_request.delete()
            return JsonResponse({"message": "request rejected"})
        
        else:
            return JsonResponse({"message": "invalid response"})
        
manage_collaboration_request = ManageCollaborationRequestView.as_view()

            
class UserSearchView(ListView):
    template_name = "accounts/user_search.html"
    context_object_name = "users"
    paginate_by = 20
    form_class = UserSearchForm

    def get_queryset(self):
        form = UserSearchForm(self.request.GET)

        if form.is_valid():
            query = form.cleaned_data.get("query")
            if query:
                queryset = CustomUser.objects.filter(short_user_id=query)
            else:
                queryset = CustomUser.objects.all()

        else:
            queryset = CustomUser.objects.all()
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #ページネーションのために使う
        context['numbers'] = [1, 2, 3, 4]  # 配列をコンテキストに追加
        context["form"] = UserSearchForm(self.request.GET or None)
        return context

user_search = UserSearchView.as_view()


class CollaborationRequestListView(ListView):
    template_name="accounts/collaboration_request_list.html"
    context_object_name = "collaboration_requests"
    paginate_by = 20

    def get_queryset(self):
        return Collaboration.objects.filter(to_user=self.request.user,status="pending")

collaboration_request_list = CollaborationRequestListView.as_view()