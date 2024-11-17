from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

# class LoginForm(forms.Form):
#     username = forms.CharField(label="username", max_length=255)
#     password = forms.CharField(label="password", widget=forms.PasswordInput(attrs={"placeholder": "password"}))

class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "email", "password")
        widgets = {"password": forms.PasswordInput(attrs={"palaceholder": "password"})}
    
    password2 = forms.CharField(label="confirmation password", required=True, widget=forms.PasswordInput(attrs={"placeholder": "again"}))

    def __init__(self, *args, **kwargs):
        super.__init__(*args, **kwargs)
        self.fields["username"].widget.attrs = {"placeholder": "username"}
        self.fields["email"].required = True
        self.fields["email"].widget.attrs = {"placeholder": "email"}
