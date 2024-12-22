from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import CreateView, ListView, DetailView
from .forms import ImportPaperForm, SearchPaperForm
from .models import Paper, Author
from django.urls import reverse_lazy
from datetime import datetime
from django.db.models import Q

import requests
import xml.etree.ElementTree as ET

#from crossref.restful import Works
CROSSREF_API_URL = "https://api.crossref.org/works"

#import arxiv
ARXIV_API_URL = "http://export.arxiv.org/api/query"

# Create your views here.

class ImportPaperView(CreateView):
    model = Paper
    form_class = ImportPaperForm
    template_name = "papers/import_paper.html"

    def get_success_url(self):
        if self.kwargs.get("project_id"):
            return reverse_lazy("research_projects:add_search_paper", project_id=self.kwargs.get())
        else:
            return reverse_lazy("papers:paper_list")

    def form_valid(self, form):
        if form.cleaned_data.get('switch') == "arxiv":
            paper = form.save(commit=False)
            arxiv_id = paper.arxiv
            params = {
                'search_query': arxiv_id,  # 特定の論文をarxiv IDで検索
                'max_results': 1,                  # 最大結果件数を1件に設定
            }
            response = requests.get(ARXIV_API_URL, params)
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                entries = root.findall('{http://www.w3.org/2005/Atom}entry')

                if entries:
                    for entry in entries:
                        paper.title = entry.find('{http://www.w3.org/2005/Atom}title').text
                        authors = []
                        for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
                            name = author.find('{http://www.w3.org/2005/Atom}name')
                            if name is not None:
                                # すでに存在する著者を取得、なければ新規作成
                                first_name = " ".join(name.text.split(" ")[:-1])
                                last_name = name.text.split(" ")[-1]
                                author_instance, created = Author.objects.get_or_create(first_name=first_name, last_name=last_name)
                                authors.append(author_instance)
                        published_str = entry.find('{http://www.w3.org/2005/Atom}published').text
                        paper.published_date = datetime.fromisoformat(published_str[:-1]).date()
            paper.save()
            paper.authors.set(authors) 
            return super().form_valid(form)
        
        elif form.cleaned_data.get('switch') == "DOI":
            paper = form.save(commit=False)
            doi = paper.doi
            request_url = f"{CROSSREF_API_URL}/{doi}"
            response = requests.get(request_url)
            if response.status_code == 200:
                data = response.json()
                message = data["message"]
                paper.title = message["title"][0]
                authors = []
                for author in message["author"]:
                    first_name = f"{author['given']}"
                    last_name = f"{author['family']}"
                    author_instance, created = Author.objects.get_or_create(first_name=first_name, last_name=last_name)
                    authors.append(author_instance)
        
                arxiv_id = None
                links = message.get("link", [])
                for link in links:
                    if "arxiv" in link["URL"]:
                        arxiv_id = link["URL"].split("/")[-1]
                        break
                paper.arxiv = arxiv_id
                published_parts = message["published"]["date-parts"][0]
                ymd = [1,1,1]
                for i in range(len(published_parts)):
                    ymd[i] = published_parts[i]
                paper.published_date = datetime(ymd[0], ymd[1], ymd[2]).date()

            paper.save()
            paper.authors.set(authors)
            return super().form_valid(form)

import_paper = ImportPaperView.as_view()


class PaperDetailView(DetailView):
    model = Paper
    template_name = "papers/paper_detail.html"
    context_object_name = "paper"

    def get_object(self, queryset=None):
        # URLからproject_idを取得して、それを元にProjectオブジェクトを取得
        paper_id = self.kwargs.get('paper_id')
        return get_object_or_404(Paper, paper_id=paper_id)

paper_detail = PaperDetailView.as_view()


class PaperListView(ListView):
    template_name = "papers/paper_list.html"
    context_object_name = "papers"
    paginate_by = 20

    def get_queryset(self):
        form = SearchPaperForm(self.request.GET)
        queryset = Paper.objects.all()
        if "query" in self.request.GET:
            if form.is_valid():
                query = form.cleaned_data.get("query")
                if query:
                    queryset = queryset.filter(Q(title__icontains=query) | Q(arxiv__icontains=query) | Q(doi__icontains=query))
        else:
            queryset = Paper.objects.all()
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #ページネーションのために使う
        context['numbers'] = [1, 2, 3, 4]  # 配列をコンテキストに追加

        context["form"] = SearchPaperForm(self.request.GET or None)
        if "query" in self.request.GET:
            query = self.request.GET.get("query", "").strip()
            if query:
                context["message"] = f"検索結果： {query}"
            else:
                context["message"] = "全ての結果" 
        else:
            context["message"] = "全ての結果"
        return context

paper_list = PaperListView.as_view()