from django.db import models
from datetime import datetime  # 导入datetime 用于处理上传文件的时间字段
from django.contrib.auth.models import AbstractBaseUser


# Create your models here.
# 如果要将一个普通的类变成一个可以映射到数据库中的ORM模型
# 那么必须要将父类设置为models.Model或者它的子类


class Author(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()


class Publisher(models.Model):
    name = models.CharField(max_length=300)
    num_awards = models.IntegerField()


class Book(models.Model):
    # 1. id：int类型，自增长（不设置也会自动生成）
    # 2. name：varchar(300)，图书名
    # 3. price：固定精度的十进制数 价格
    # 4. pages: 页数，默认为0
    # 5. rating: 评分，可为null
    # pubdate: 每次保存对象时自动将字段设置为现在。
    name = models.CharField(max_length=300)
    pages = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField(null=True)
    authors = models.ManyToManyField(Author)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, default=1)
    pubdate = models.DateField(auto_now=True)

    # 打印模型对象返回的字段
    def __str__(self):
        # <Book:(name,author,price)>
        return "<Book:({name},{author},{price})>".format(name=self.name, author=self.authors, price=self.price)


class Store(models.Model):
    name = models.CharField(max_length=300)
    books = models.ManyToManyField(Book)
    registered_users = models.PositiveIntegerField()


class Film(models.Model):
    name = models.CharField(max_length=30)
    length = models.IntegerField(default=0)
    releaseday = models.DateField()
    boxoffice_tot = models.BigIntegerField(default=0)
    tags = models.ManyToManyField('Tag', related_name="films")
    regions = models.ManyToManyField('Region', related_name="films")


class Region(models.Model):
    name = models.CharField(max_length=30, unique=True)


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)


class Upload(models.Model):
    DownloadDocount = models.IntegerField(verbose_name=u"访问次数", default=0)
    # 访问该页面的次数 IntegerField 表示整数字段
    code = models.CharField(max_length=8, verbose_name=u"code")
    # 唯一标识一个文件 CharField 表示字符串字段
    Datatime = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")
    # Datatime 表示文件上传的时间，其中datetime.now 不能加括号,否则时间
    # 就变成了orm生成model的时间, 这里一定要注意！！
    path = models.CharField(max_length=32, verbose_name=u"下载路径")
    # path 代表文件存储的路径
    name = models.CharField(max_length=32, verbose_name=u"文件名", default="")
    # name 文件名
    Filesize = models.CharField(max_length=10, verbose_name=u"文件大小")
    # Filesize 文件大小
    PCIP = models.CharField(max_length=32, verbose_name=u"IP地址", default="")

    # PCIP 上传文件的IP

    class Meta:  # Meta 可用于定义数据表名，排序方式等。
        verbose_name = "download"  # 指明一个易于理解和表示的单词形式的对象。
        db_table = "download"  # 声明数据表的名。

    def __str__(self):  # 表示在做查询操作时，我们看到的是 name 字段
        return self.name


class User(AbstractBaseUser):
    AdminType = (
        ('REGULAR_USER', "Regular User"),
        ('VIP_USER', "Vip User")
    )
    username = models.CharField(max_length=128, unique=True)
    email = models.EmailField(unique=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    # One of UserType
    admin_type = models.CharField(max_length=32, choices=AdminType, default="Regular User")

    def is_vip_user(self):
        return self.admin_type == 'VIP_USER'

    class Meta:
        db_table = "user"



'''
1. 使用makemigrations生成迁移脚本文件
python mange.py makemigrations [appname]

2. 使用migrate 将生成的迁移脚本文件映射到数据库中
python manage.py migrate [appname]
'''
