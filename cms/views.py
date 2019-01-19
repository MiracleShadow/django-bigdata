from django.http import HttpResponse


def index(request):
    return HttpResponse('CMS首页')


def login(request):
    return HttpResponse('CMS登陆页面')
