from django import forms


class UserForm(forms.Form):
    username = forms.CharField(label='', min_length=2, max_length=8,
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control', 'placeholder': "用户名", 'autofocus': ''}))
    password = forms.CharField(label='', min_length=6, max_length=16,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "密码"}))


class RegisterForm(forms.Form):
    username = forms.CharField(label='用户名', min_length=2, max_length=8,
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control', 'placeholder': "用户名", 'autofocus': ''}))
    email = forms.EmailField(label='邮箱地址',
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "邮箱地址"}))
    password1 = forms.CharField(label='密码', min_length=6, max_length=16,
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "密码"}))
    password2 = forms.CharField(label='确认密码', min_length=6, max_length=16,
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "确认密码"}))
