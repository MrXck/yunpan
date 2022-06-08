from django import forms
from django.core.exceptions import ValidationError

from utils.encrypt import md5
from web import models


class LoginForm(forms.ModelForm):
    username = forms.CharField(max_length=16, required=True, min_length=6)
    password = forms.CharField(max_length=16, required=True, min_length=6)

    class Meta:
        model = models.User
        fields = '__all__'

    def clean_password(self):
        password = self.cleaned_data.get('password')
        password = md5(password)
        username = self.cleaned_data.get('username')
        user_obj = models.User.objects.filter(username=username, password=password).first()
        if user_obj:
            self.cleaned_data['user_obj'] = user_obj
            return password
        raise ValidationError('用户名或密码错误')


class RegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=16, required=True, min_length=6)
    password = forms.CharField(max_length=16, required=True, min_length=6)
    confirm_password = forms.CharField(max_length=16, required=True, min_length=6)

    class Meta:
        model = models.User
        fields = '__all__'

    def clean_username(self):
        username = self.cleaned_data.get('username')
        user_obj = models.User.objects.filter(username=username).first()
        if user_obj:
            raise ValidationError('用户名已存在')
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        return md5(password)

    def clean_confirm_password(self):
        confirm_password = self.cleaned_data.get('confirm_password')
        confirm_password = md5(confirm_password)
        password = self.cleaned_data.get('password')
        if confirm_password != password:
            raise ValidationError('重复密码和密码不一致')
        return confirm_password
