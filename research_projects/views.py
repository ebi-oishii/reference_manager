from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, DetailView, UpdateView, ListView, FormView, DeleteView
from django.db.models import Max
from django.db import transaction
from django.http import JsonResponse
from django.views import View
from accounts.models import CustomUser, Collaboration
from .models import Project, Post, PapersIndices
from .forms import AddMemberForm, SearchMemberForm, SearchProjectForm, SearchPaperForm
from papers.models import Paper
from django.urls import reverse_lazy
from django.db.models import Q


# Create your views here.

class CreateProjectView(CreateView):
    model = Project
    template_name = "research_projects/create_project.html"
    fields = ["name", "description", "project_url"]
    
    def get_success_url(self):
        # success_url を動的に取得して返す
        return reverse_lazy('research_projects:project_detail', kwargs={'project_id': self.object.project_id})
    
    def form_valid(self, form):
        project = form.save(commit=False)
        project.save()
        
        project.members.add(self.request.user)

        return super().form_valid(form)
    
create_project = CreateProjectView.as_view()


class ProjectDetailView(DetailView):
    model = Project
    template_name = "research_projects/project_detail.html"
    context_object_name = "project"

    def get_object(self, queryset=None):
        # URLからproject_idを取得して、それを元にProjectオブジェクトを取得
        project_id = self.kwargs.get('project_id')
        return get_object_or_404(Project, project_id=project_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["members_short_list"] = self.object.members.all()[:5]
        context["posts_short_list"] = self.object.posts.all().order_by("-posted_on")[:5]
        return context

project_detail = ProjectDetailView.as_view()


class AddSearchMemberView(ListView):
    model = CustomUser
    template_name = "research_projects/add_search_member.html"
    context_object_name = "collaborators"
    paginate_by = 20

    def get_queryset(self):
        form = SearchMemberForm(self.request.GET)

        if form.is_valid():
            query = form.cleaned_data.get("query")    
            collaborators_temp = Collaboration.objects.filter(Q(from_user=self.request.user, status="accepted") | Q(to_user=self.request.user, status="accepted")).values_list("from_user", "to_user")
            collaborators =[user_id  for pair in collaborators_temp  for user_id in pair  if user_id != self.request.user.user_id]
            queryset = CustomUser.objects.filter(user_id__in = collaborators)
            
            if query:
                queryset = queryset.filter(Q(username__icontains=query) | Q(user_id__icontains=query) | Q(short_user_id__icontains=query))
                return queryset
            else:
                return queryset
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_id"] = self.kwargs.get("project_id")
        #ページネーションのために使う
        context['numbers'] = [1, 2, 3, 4]
        return context

add_search_member = AddSearchMemberView.as_view()


class AddMemberView(View):
    def post(self, request, *args, **kwargs):
        project_id = kwargs.get("project_id")
        project = get_object_or_404(Project, project_id=project_id)
        added_user_id = kwargs.get("user_id")
        added_user = get_object_or_404(CustomUser, user_id=added_user_id)
        try:
            with transaction.atomic():
                if added_user in project.members.all():
                    return JsonResponse({"message": f"{added_user.username}はすでにプロジェクトメンバーです"})
                else:
                    project.save()
                    project.members.add(added_user)
                    return JsonResponse({"message": f"{added_user.username}を追加しました"})
        except Exception as e:
            return JsonResponse({"error": "メンバー追加中にエラーが発生しました。", "details": str(e)}, status=500)

add_member = AddMemberView.as_view()


class AddSearchPaperView(ListView):
    model = Paper
    template_name = "research_projects/add_search_paper.html"
    context_object_name = "papers"
    paginate_by = 20

    def get_queryset(self):
        form = SearchPaperForm(self.request.GET)

        if form.is_valid():
            query = form.cleaned_data.get("query")
            if query:
                queryset = Paper.objects.all()
                queryset = queryset.filter(Q(title__icontains=query) | Q(arxiv__icontains=query) | Q(doi__icontains=query))
            else:
                queryset = Paper.objects.all()

        else:
            queryset = Paper.objects.all()
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = SearchPaperForm(self.request.GET)
        context["project_id"] = self.kwargs.get("project_id")
        #ページネーションのために使う
        context['numbers'] = [1, 2, 3, 4]
        return context

add_search_paper = AddSearchPaperView.as_view()


class AddPostView(CreateView):
    model = Post
    template_name = "research_projects/add_post.html"
    context_object_name = "papers"
    fields = ["content"]

    def get_project(self):
        project_id = self.kwargs.get("project_id")
        return get_object_or_404(Project, project_id=project_id)

    def get_success_url(self):
        project = self.get_project()
        return reverse_lazy('research_projects:project_detail', kwargs={"project_id": project.project_id})

    def form_valid(self, form):
        post = form.save(commit=False)
        post.contributer = self.request.user
        post.project = self.get_project()
        post.save()
        return super().form_valid(form)
    
add_post = AddPostView.as_view()


class AddPaperView(View):
    def post(self, request, *args, **kwargs):
        paper_id = kwargs.get("paper_id")
        paper = get_object_or_404(Paper, paper_id=paper_id)
        project_id = kwargs.get("project_id")
        project = get_object_or_404(Project, project_id=project_id)
        try:
            with transaction.atomic():
                i = PapersIndices.objects.filter(project=project).aggregate(Max("index"))["index__max"]
                if i is None:
                    i = 1
                else:
                    i = i + 1
            paper_index , created = PapersIndices.objects.get_or_create(project=project, paper=paper, index=i)
            if created:
                paper_index.save()
                return JsonResponse({"message": f"{paper.title}を追加しました"})
            else:
                return JsonResponse({"message": "追加に失敗"})
        
        except Exception as e:
            # エラーハンドリング
            return JsonResponse({"error": "追加処理中にエラーが発生しました。", "details": str(e)}, status=500)

add_paper = AddPaperView.as_view()
            

class EditCitationView(UpdateView):
    model = PapersIndices
    fields = ["description"]
    template_name = "research_projects/edit_citation.html"

    def get_project(self):
        project_id = self.kwargs.get("project_id")
        project = get_object_or_404(Project, project_id=project_id)
        return project

    def get_object(self):
        project = self.get_project()
        index = self.kwargs.get("index")
        paper_index = get_object_or_404(PapersIndices, project=project, index=index)
        return paper_index
    
    def get_success_url(self):
        project = self.get_project()
        return reverse_lazy('research_projects:project_detail', kwargs={"project_id": project.project_id})
    
edit_citation = EditCitationView.as_view()


class ProjectListView(ListView):
    template_name = "research_projects/project_list.html"
    context_object_name = "projects"
    paginate_by = 20

    def get_queryset(self):
        form = SearchProjectForm(self.request.GET)
        queryset = Project.objects.filter(is_public=True).order_by("-updated_at")
        if "query" in self.request.GET:
            if form.is_valid():
                query = form.cleaned_data.get("query")
                if query:
                    queryset = Project.objects.filter(is_public=True)
                    queryset = queryset.filter(name__icontains=query) | queryset.filter(description__icontains=query) | queryset.filter(short_project_id__icontains=query) | queryset.filter(project_id__icontains=query)
        else:
            if self.request.user.is_authenticated:
                queryset = Project.objects.filter(is_public=True, bookmark_user=self.request.user)
            else:
                queryset = Project.objects.none()
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #ページネーションのために使う
        context['numbers'] = [1, 2, 3, 4]  # 配列をコンテキストに追加

        context["form"] = SearchProjectForm(self.request.GET or None)
        if "query" in self.request.GET:
            query = self.request.GET.get("query", "").strip()
            if query:
                context["message"] = f"検索結果： {query}"
            else:
                context["message"] = "全ての結果" 
        else:
            context["message"] = "ブックマークされたプロジェクト"
        return context

project_list = ProjectListView.as_view()


class PublicSwitchView(View):
    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, project_id=kwargs.get("project_id"))
        
        if request.POST.get("toggle_public") == "on":
            project.is_public = True
            project.save()
            return JsonResponse({"message": "プロジェクトを公開に切り替えました"})
        
        elif request.POST.get("toggle_public") == None:
            project.is_public = False
            project.save()
            return JsonResponse({"message": "プロジェクトを非公開に切り替えました"})
        
        else:
            return JsonResponse({"message": "無効なリクエストです"})
        
public_switch = PublicSwitchView.as_view()


class VisibleSwitchView(View):
    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, project_id=kwargs.get("project_id"))
        
        if request.POST.get("toggle_visible") == "on":
            project.is_visible = True
            project.save()
            return JsonResponse({"message": "プロジェクトを可視に切り替えました"})
        
        elif request.POST.get("toggle_visible") == None:
            project.is_visible = False
            project.save()
            return JsonResponse({"message": "プロジェクトを不可視に切り替えました"})

        
visible_switch = VisibleSwitchView.as_view()


class ChangeURLView(UpdateView):
    model = Project
    fields = ["project_url",]
    template_name = "research_projects/change_url.html"

    def get_success_url(self):
        return reverse_lazy("research_projects:project_detail", kwargs={"project_id": self.kwargs.get("project_id")})
    
    def get_object(self):
        return get_object_or_404(Project, project_id=self.kwargs.get("project_id"))
    
change_url = ChangeURLView.as_view()


class ChangeDescriptionView(UpdateView):
    model = Project
    fields = ["description", ]
    template_name = "research_projects/change_description.html"

    def get_success_url(self):
        return reverse_lazy("research_projects:project_detail", kwargs={"project_id": self.kwargs.get("project_id")})

    def get_object(self):
        return get_object_or_404(Project, project_id=self.kwargs.get("project_id"))
    
change_description = ChangeDescriptionView.as_view()


class DeleteProjectView(DeleteView):
    model = Project
    template_name = "research_projects/delete_confirmation.html"

    def get_object(self):
        return get_object_or_404(Project, project_id=self.kwargs.get("project_id"))

    def get_success_url(self):
        return reverse_lazy("accounts:profile", kwargs={"profile_username": self.request.user.username})
    
delete_project = DeleteProjectView.as_view()


class PostListView(ListView):
    template_name = "reseach_projects/post_list.html"
    context_object_name = "posts"
    paginate_by = 20

    def get_queryset(self):
        queryset = Post.objects.filter(project=self.kwargs.get("project_id")).order_by("posted_on")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #ページネーションのために使う
        context['numbers'] = [1, 2, 3, 4]  # 配列をコンテキストに追加
        return context
    
post_list = PostListView.as_view()