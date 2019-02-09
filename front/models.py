from django.db import models


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
        return "<Book:({name},{author},{price})>".format(name=self.name, author=self.author, price=self.price)


class Store(models.Model):
    name = models.CharField(max_length=300)
    books = models.ManyToManyField(Book)
    registered_users = models.PositiveIntegerField()


'''
1. 使用makemigrations生成迁移脚本文件
python mange.py makemigrations [appname]

2. 使用migrate 将生成的迁移脚本文件映射到数据库中
python manage.py migrate [appname]
'''
