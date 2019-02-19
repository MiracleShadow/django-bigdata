from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.template.loader import render_to_string
from datetime import datetime
from django.db import connection
from .models import Film
from .models import Tag
from .models import Region
import pandas as pd
import requests


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
    # ?username=xxx
    connection_mysql_db(request)
    username = request.GET.get('username')
    context = {
        'username': username,
        "today": datetime.now()
    }
    if username:
        # html = render_to_string("base.html")
        # return HttpResponse(html)
        return render(request, 'index.html', context=context)
    else:
        # 多个app中出现同名url，使用应用命名空间解决冲突问题
        login_url = reverse('front:login')
        return redirect(login_url)


def login(request):
    return render(request, 'signin.html')


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


def yunpan(request):
    return render(request, 'yunpan.html')


def connection_mysql_db(request):
    cursor = connection.cursor()
    cursor.execute("show tables")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    cursor.close()
    return render(request, 'index.html')
