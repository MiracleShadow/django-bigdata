from django.urls import path
from . import views

# 应用命名空间
# 应用命名空间的变量叫做app_name
app_name = 'front'

urlpatterns = [
    # url是经常变化的，如果在代码中写死，可能会经常改代码
    # 给url取个名字'name=xxx'，以后使用url的时候就使用它的名字进行反转就可以了reverse
    # 若多个app中出现同名url，使用应用命名空间可解决冲突问题
    path('', views.index, name='index'),
    path('if_test/', views.if_test, name='if_test'),
    path('for_test/', views.for_test, name='for_test'),
    path('book/', views.book, name='book'),
    path('book/detail/<book_id>/<category>', views.book_detail, name='book_detail'),
    path('movie/', views.movie, name='movie'),
    path('city', views.city, name='city'),
    path('signin/', views.login, name='login'),
    path('add/', views.add_view),
    path('cut/', views.cut_view),
    path('date/', views.date_view),
]
