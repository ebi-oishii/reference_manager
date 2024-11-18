from django import forms
from dal import autocomplete
from .models import Project, PapersIndices


# class CreateProjectForm(forms.ModelForm):
#     class Meta:
#         model = Project

class AddPaperForm(forms.ModelForm):
    class Meta:
        model = PapersIndices
        fields = ["paper",]
        widgets = {"paper": autocomplete.ModelSelect2(url="research_projects:paper-autocomplete"),}