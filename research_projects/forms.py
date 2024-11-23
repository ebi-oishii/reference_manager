from django import forms
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Project, PapersIndices
from accounts.models import Collaboration


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

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        project = kwargs.pop("project")
        super().__init__(*args, **kwargs)

        if user:
            collaborators = Collaboration.objects.filter((Q(from_user=user) | Q(to_user=user)), status="accepted").values_list("from_user", "to_user")
            accepted_users = [user_id   for pair in collaborators    for user_id in pair    if user_id != user.user_id]
            existing_members = project.members.all().values_list("user_id", flat=True)
            self.fields["members"].queryset = get_user_model().objects.filter(user_id__in=accepted_users).exclude(user_id__in=existing_members)



class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, label='keyword')