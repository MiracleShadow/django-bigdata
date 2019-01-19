from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.template.loader import render_to_string


def index(request):
    # ?username=xxx
    username = request.GET.get('username')
    if username:
        # html = render_to_string("index.html")
        # return HttpResponse(html)
        return render(request, 'index.html')
    else:
        # 多个app中出现同名url，使用应用命名空间解决冲突问题
        login_url = reverse('front:login')
        return redirect(login_url)


def login(request):
    return HttpResponse('前台登陆页面')
