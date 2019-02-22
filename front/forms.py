from django import forms


class UserForm(forms.Form):
    username = forms.CharField(label='', max_length=128,
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control', 'placeholder': "用户名", 'autofocus': ''}))
    password = forms.CharField(label='', max_length=256,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "密码"}))


class RegisterForm(forms.Form):
    username = forms.CharField(label='', max_length=128,
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control', 'placeholder': "用户名", 'autofocus': ''}))
    email = forms.EmailField(label='',
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "邮箱地址"}))
    password1 = forms.CharField(label='', max_length=256,
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "密码"}))
    password2 = forms.CharField(label='', max_length=256,
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "确认密码"}))
