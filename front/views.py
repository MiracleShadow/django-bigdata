from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.template.loader import render_to_string


class Person(object):
    def __init__(self, username):
        self.username = username


def index(request):
    # ?username=xxx
    username = request.GET.get('username')
    # p = Person("MiracleShadow")
    # context = {
    #     'person': p
    # }
    context = {
        'person': {
            'username': 'MiracleShadow',
            'age': 21,
            'height': 180
            # 不能使用'keys', 'values'这样的可能产生歧义的属性
            # 因为访问一个字典的key对应的value，只能通过'字典.keys'的方式进行访问
            # 列表、元组同理
        },
        'persons': [
            '张三',
            '李四',
            '王五'
        ],
        'books': [
            {
                'name': '三国演义',
                'author': '罗贯中',
                'price': 100
            },
            {
                'name': '水浒传',
                'author': '施耐庵',
                'price': 99
            },
            {
                'name': '西游记',
                'author': '吴承恩',
                'price': 150
            },
            {
                'name': '红楼梦',
                'author': '曹雪芹',
                'price': 200
            },
        ]
    }
    if True:
        # html = render_to_string("index.html")
        # return HttpResponse(html)
        return render(request, 'index.html', context=context)
    else:
        # 多个app中出现同名url，使用应用命名空间解决冲突问题
        login_url = reverse('front:login')
        return redirect(login_url)


def login(request):
    return HttpResponse('前台登陆页面')
