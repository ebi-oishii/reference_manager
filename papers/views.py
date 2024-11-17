from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView
from .forms import ImportPaperForm
from .models import Paper, Author
from django.urls import reverse_lazy
from datetime import datetime

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
    success_url = reverse_lazy("accounts:index")

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