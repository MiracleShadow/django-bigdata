from django.shortcuts import render
from django.http import HttpResponsePermanentRedirect, HttpResponse
from django.shortcuts import redirect, reverse
from django.template.loader import render_to_string
from django.views.generic import View  # 这是Django给我们的视图类
from datetime import datetime
from django.db import connection
from django import forms
from .models import Film
from .models import Tag
from .models import Region
from .models import Upload
from .models import User
from .forms import UserForm
from .forms import RegisterForm
import pandas as pd
import requests
import random
import string
import json


class Person(object):
    def __init__(self, username):
        self.username = username


class Page(object):
    def __init__(self, page_num, total_count, url_prefix, per_page=10, max_page=11):
        """
        :param page_num:    当前页码数
        :param total_count: 数据总数
        :param url_prefix:  a标签href的前缀
        :param per_page:    每页显示多少条数据
        :param max_page:    页面上最多显示几个页码
        """
        self.url_prefix = url_prefix
        # 需要多少页展示
        self.total_page = (total_count - 1) // per_page + 1
        try:
            self.page_num = min(int(page_num), self.total_page)
            # 如果输入的也么书超过了最大的页码数，默认返回最后一页
        except Exception as e:
            # 当输入的页码不是正经数字的时候
            self.page_num = 1

        # 定义两个变量保存数据从哪儿取到哪儿
        self.data_start = (page_num - 1) * per_page
        self.data_end = page_num * per_page

        # 页面上总共展示多少页码
        if page_num - (max_page // 2) < 1:
            self.page_start, self.page_end = 1, max_page
        elif page_num + (max_page // 2) > self.total_page:
            self.page_start, self.page_end = self.total_page - max_page, self.total_page
        else:
            self.page_start = max(page_num - max_page // 2, 1)
            self.page_end = min(page_num + max_page // 2, self.total_page)

    @property
    def start(self):
        return self.data_start

    @property
    def end(self):
        return self.data_end

    def page_html(self):
        html_str_list = ['<li><a href="{url}?page=1">首页</a></li>'.format(url=self.url_prefix)]

        # 如果是第一页就没有上一页
        if self.page_num <= 1:
            html_str_list.append(
                '<li class="disable"><a href="#" aria-label="Previous">'
                '<span aria-hidden="true">&laquo;</span></a></li>')
        else:
            html_str_list.append(
                '<li><a href="{0}?page={1}" aria-label="Previous">'
                '<span aria-hidden="true">&laquo;</span></a></li>'.format(
                    self.url_prefix, self.page_num - 1))

        for i in range(self.page_start, self.page_end + 1):
            # 如果是当前页就加active样式类
            if i == self.page_num:
                tmp = '<li class="active"><a href="{url}?page={page_num}">{page_num}</a></li>'.format(
                    url=self.url_prefix, page_num=i)
            else:
                tmp = '<li><a href="{url}?page={page_num}">{page_num}</a></li>'.format(url=self.url_prefix, page_num=i)
            html_str_list.append(tmp)

        # 如果是最后一页就没有下一页
        if self.page_num >= self.total_page:
            html_str_list.append(
                '<li class="disable"><a href="#" aria-label="Previous">'
                '<span aria-hidden="true">&raquo;</span></a></li>')
        else:
            html_str_list.append(
                '<li><a href="{0}?page={1}" aria-label="Previous">'
                '<span aria-hidden="true">&raquo;</span></a></li>'.format(
                    self.url_prefix, self.page_num + 1))

        html_str_list.append(
            '<li><a href="{url}?page={page_num}">尾页</a></li>'.format(
                url=self.url_prefix, page_num=self.total_page))
        page_html = "".join(html_str_list)
        return page_html


class Weather(object):
    def __init__(self, key='xm0y41jwmnke1tdi', city_name='boxing'):
        # 天气API文档：https://www.seniverse.com/doc
        self.key = key
        self.weather_now_url = 'https://api.seniverse.com/v3/weather/now.json?' \
                               'key={key}&location={city_name}&language=zh-Hans&unit=c'.format(key=key,
                                                                                               city_name=city_name)
        self.alarm_url = 'https://api.seniverse.com/v3/weather/alarm.json?' \
                         'key={key}&location={city_name}'.format(key=key, city_name=city_name)
        self.weather_daily_url = 'https://api.seniverse.com/v3/weather/daily.json' \
                                 '?key={key}&location={city_name}&language=zh-Hans'.format(key=key, city_name=city_name)

    def context(self):
        try:
            weather_now = requests.get(self.weather_now_url, timeout=4)
            weather_now_text = weather_now.json()['results'][0]
            location = weather_now_text['location']
            now = weather_now_text['now']
            last_update = weather_now_text['last_update']
            weather_now_api = True
        except requests.exceptions.RequestException:
            weather_now_api = False
            now, location, last_update = {}, {}, {}
        except Exception:
            weather_now_api = False
            now, location, last_update = {}, {}, {}

        try:
            alarm = requests.get(self.alarm_url, timeout=4)
            alarm_api = True
            alarm_text = alarm.json()['results'][0]
            # 该城市所有的灾害预警数组
            alarms = alarm_text['alarms']
            alarms_len = len(alarms)
            if alarms_len == 0:
                alarms = [{'description': '暂无信息'}]
        except requests.exceptions.RequestException:
            alarm_api = False
            alarms = []
        except Exception:
            alarm_api = False
            alarms = []

        try:
            weather_daily = requests.get(self.weather_daily_url, timeout=4)
            weather_daily_text = weather_daily.json()['results'][0]
            daily = weather_daily_text['daily']
            daily_len = len(daily)
            weather_daily_api = True
        except requests.exceptions.RequestException:
            weather_daily_api = False
            daily_len = 0
            daily = []
        except Exception as e:
            print(e)
            weather_daily_api = False
            daily_len = 0
            daily = []

        context = {
            'weather_now_api': weather_now_api,
            'now': now,
            'location': location,
            'last_update': last_update,
            'alarm_api': alarm_api,
            'alarms': alarms,
            'weather_daily_api': weather_daily_api,
            'daily_len': daily_len,
            'daily': daily,
        }
        return context


def index(request):
    # if not request.session.get('is_login', None):
    #     # 多个app中出现同名url，使用应用命名空间解决冲突问题
    #     login_url = reverse('front:login')
    #     return redirect(login_url)
    return render(request, 'index.html')


def login(request):
    # 不允许重复登录
    if request.session.get('is_login', None):
        return redirect(reverse('front:index'))

    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "请检查填写的内容，所有字段都必须填写！"
        # 使用表单类自带的is_valid()方法一步完成数据验证工作
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            # 验证成功后可以从表单对象的cleaned_data数据字典中获取表单的具体值
            print('验证成功')
            if username and password:  # 确保邮箱和密码都不为空
                username = username.strip()
                # 用户名字符合法性验证
                # 密码长度验证
                # 更多的其它验证.....
                try:
                    user = User.objects.get(username=username)
                    if user.password == password:
                        print("登陆成功！跳转主页……")
                        request.session['is_login'] = True
                        request.session['user_id'] = user.id
                        request.session['user_name'] = user.username
                        return redirect(reverse('front:index'))
                    else:
                        message = "密码不正确！"
                except Exception as e:
                    print(e)
                    message = "用户名不存在！"
        return render(request, 'signin.html', locals())
        # 如果验证不通过，则返回一个包含先前数据的表单给前端页面，方便用户修改。
        # 也就是说，它会帮你保留先前填写的数据内容，而不是返回一个空表！
    login_form = UserForm()
    return render(request, 'signin.html', locals())
    # 对于非POST方法发送数据时，比如GET方法请求页面，返回空的表单，让用户可以填入数据


'''
Python内置了一个locals()函数，它返回当前所有的本地变量字典，
我们可以偷懒的将这作为render函数的数据字典参数值，就不用费劲去构造一个形如{'message':message, 'login_form':login_form}的字典了。
这样做的好处当然是大大方便了我们，但是同时也可能往模板传入了一些多余的变量数据，造成数据冗余降低效率。
'''


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect(reverse('front:index'))
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect(reverse('front:index'))


def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/index/")
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'register.html', locals())
            else:
                same_name_user = User.objects.filter(username=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'register.html', locals())
                same_email_user = User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'register.html', locals())

                # 当一切都OK的情况下，创建新用户

                new_user = User()
                new_user.username = username
                new_user.password = password1
                new_user.email = email
                new_user.save()
                return redirect('/signin/')  # 自动跳转到登录页面
    register_form = RegisterForm()
    return render(request, 'register.html', locals())


def get_cursor():
    return connection.cursor()


def book(request):
    # # 1. 使用ORM添加一条数据到数据库中
    # book = Book(name='三国演义', author='罗贯中', price=200)
    # book.save()

    # 2. 查询
    # 2.1 根据主键进行查找
    # book = Book.objects.get(id=2)
    # print(book)
    # 2.2 根据其他条件进行查找
    # books = Book.objects.filter(name='西游记').first()
    # print(books)

    # 3. 删除数据
    # book = Book.objects.get(pk=1)
    # book.delete()

    # 4. 修改数据
    # book = Book.objects.get(pk=2)
    # book.price = 200
    # book.save()

    try:
        cursor = get_cursor()
        try:
            cursor.execute("select * from front_film")
            books = cursor.fetchall()
            cursor.close()
            return render(request, 'book.html', context={'books': books})
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)


def add_movie():
    df = pd.read_csv('E:/WebSpider/2017films.csv', encoding='gbk')
    for row in df.iterrows():
        name = row[1]['mname']
        tags = row[1]['tag'].split(',')
        length = row[1]['mlength']
        releaseday = row[1]['releaseday']
        regions = row[1]['region'].split('/')
        boxoffice_tot = row[1]['boxoffice_tot']

        film = Film(name=name, length=length,
                    releaseday=datetime.strptime(releaseday, '%Y-%m-%d'),
                    boxoffice_tot=int(boxoffice_tot))
        film.save()

        for re in regions:
            r = Region(name=re)
            try:
                r.save()
                film.regions.add(r)
            except Exception as e:
                pass

        for tag in tags:
            t = Tag(name=tag)
            try:
                t.save()
                film.tags.add(t)
            except Exception as e:
                pass

        film.save()


def movie(request):
    # 从url获取参数
    page_num = int(request.GET.get("page")) if request.GET.get("page") is not None else 1
    # 总数据是多少
    total_count = Film.objects.all().count()
    page_obj = Page(page_num, total_count, url_prefix='/movie/', per_page=10, max_page=10)
    all_films = Film.objects.all()[page_obj.start: page_obj.end]
    return render(request, 'movie.html', {"films": all_films, "page_html": page_obj.page_html()})


def city(request):
    if request.method == 'GET':
        city_name = request.GET.get("name") if request.GET.get("name") is not None else 'boxing'
    else:
        city_name = request.POST.get("text")
        if len(city_name) == 0:
            city_name = 'boxing'
    weather_context = Weather(city_name=city_name).context()
    return render(request, 'city.html', context=weather_context)


def for_test(request):
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
    return render(request, 'for_test.html', context=context)


def if_test(request):
    # p = Person('MiracleShadow')
    context = {
        # 'person': p,
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
    }
    return render(request, 'if_test.html', context=context)


def add_view(request):
    context = {
        'value1': ['1', '2', '3'],
        'value2': [4, 5, 6],
    }
    return render(request, 'add.html', context=context)


def cut_view(request):
    return render(request, 'cut.html')


def date_view(request):
    context = {
        "today": datetime.now(),
    }
    return render(request, 'date.html', context=context)


def company(request):
    return render(request, 'company.html')


class YunpanForm(forms.Form):
    # label: 在网页上显示的label标签信息，为空则不显示
    # error_messages: 错误信息
    file = forms.FileField(label='', error_messages={'required': '必须要选择一个文件'})


class Yunpan(View):
    def get(self, request):
        print('yunpan get')
        form = YunpanForm()
        return render(request, "yunpan.html", {'form': form})

    def post(self, request):
        print('yunpan post')
        form = YunpanForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            name = file.name
            size = int(file.size)
            code = ''.join(random.sample(string.digits, 8))

            with open('./static/file/' + name, 'wb') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
                # 遍历UploadedFile.chunks()，而不是直接使用read()方法，
                # 能确保大文件不会占用系统过多的内存。

            u = Upload(
                path='static/file/' + name,
                name=name,
                Filesize=size,
                code=code,
                PCIP=str(request.META['REMOTE_ADDR']),
            )
            u.save()
            return HttpResponsePermanentRedirect("/s/" + code)


class DisplayView(View):
    def get(self, request, code):
        u = Upload.objects.filter(code=str(code))
        if u:
            for i in u:
                i.DownloadDocount += 1
                i.save()
        # 访问一次，DownloadDocount字段自增一次
        return render(request, 'content.html', {"content": u})


class MyView(View):
    def get(self, request):
        IP = request.META['REMOTE_ADDR']
        u = Upload.objects.filter(PCIP=str(IP))
        for i in u:
            i.DownloadDocount += 1
            i.save()
        return render(request, 'content.html', {"content": u})


class SearchView(View):
    def get(self, request):
        code = request.GET.get("kw")
        u = Upload.objects.filter(name=str(code))
        data = {}
        if u:
            for i in range(len(u)):
                u[i].DownloadDocount += 1
                u[i].save()
                data[i] = {}
                data[i]['download'] = u[i].DownloadDocount
                data[i]['filename'] = u[i].name
                data[i]['id'] = u[i].id
                data[i]['ip'] = str(u[i].PCIP)
                data[i]['size'] = u[i].Filesize
                data[i]['time'] = str(u[i].Datatime.strftime('%Y-%m-%d %H:%M:%S'))
                data[i]['key'] = u[i].code
        return HttpResponse(json.dumps(data), content_type="application/json")


def connection_mysql_db(request):
    cursor = connection.cursor()
    cursor.execute("show tables")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    cursor.close()
    return render(request, 'index.html')
