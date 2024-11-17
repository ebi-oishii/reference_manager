from django import forms
from .models import Paper

class ImportPaperForm(forms.ModelForm):
    switch = forms.ChoiceField(choices=[("arxiv", "arxiv"), ("DOI", "DOI")], required=True, widget=forms.RadioSelect)
    
    class Meta:
        model = Paper
        fields = ['arxiv', 'doi']
