from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, DetailView, UpdateView
from django.db.models import Max
from .models import Project, Post, PapersIndices
from django.urls import reverse_lazy

# Create your views here.

class CreateProjectView(CreateView):
    model = Project
    template_name = "research_projects/create_project.html"
    fields = ["name", "description", "project_url"]
    
    def get_success_url(self):
        # success_url を動的に取得して返す
        return reverse_lazy('accounts:profile', kwargs={'profile_username': self.request.user.username})
    
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

project_detail = ProjectDetailView.as_view()

class AddPostView(CreateView):
    model = Post
    template_name = "research_projects/add_post.html"
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


class AddPaper(CreateView):
    model = PapersIndices
    template_name = "research_projects/add_paper.html"
    fields = ["paper"]

    def get_project(self):
        project_id = self.kwargs.get("project_id")
        return get_object_or_404(Project, project_id=project_id)

    def get_success_url(self):
        project = self.get_project()
        return reverse_lazy('research_projects:project_detail', kwargs={"project_id": project.project_id})

    def form_valid(self, form):
        paper_index = form.save(commit=False)
        project = self.get_project()
        paper_index.project = project
        try:
            i = PapersIndices.objects.filter(project=project).aggregate(Max("index"))["index__max"] + 1
        except PapersIndices.DoesNotExist:
            i = 1
        paper_index.index = i
        paper_index.save()
        return super().form_valid(form)
    
add_paper = AddPaper.as_view()


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