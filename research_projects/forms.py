from django import forms
from .models import Project, PapersIndices


# class CreateProjectForm(forms.ModelForm):
#     class Meta:
#         model = Project

# class AddPaperForm(forms.ModelForm):
#     class Meta:
#         model = PapersIndices
#         fields = ["paper",]
#         widgets = {"paper": autocomplete.ModelSelect2(url="research_projects:paper-autocomplete"),}

class AddMemberForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["members"]



class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, label='keyword')