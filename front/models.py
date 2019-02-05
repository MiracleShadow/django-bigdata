from django.db import models


# Create your models here.
# 如果要将一个普通的类变成一个可以映射到数据库中的ORM模型
# 那么必须要将父类设置为models.Model或者它的子类
class Book(models.Model):
    # 1. id：int类型，自增长（不设置也会自动生成）
    # 2. name：varchar(100)，图书名
    # 3. author：varchar(100)，作者
    # 4. price：float 价格
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    author = models.CharField(max_length=100, null=False)
    price = models.FloatField(null=False, default=0)

    # 打印模型对象返回的字段
    def __str__(self):
        # <Book:(name,author,price)>
        return "<Book:({name},{author},{price})>".format(name=self.name, author=self.author, price=self.price)


'''
1. 使用makemigrations生成迁移脚本文件
python mange.py makemigrations [appname]

2. 使用migrate 将生成的迁移脚本文件映射到数据库中
python manage.py migrate [appname]
'''
