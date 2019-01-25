from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

# 应用命名空间
# 应用命名空间的变量叫做app_name
app_name = 'QRcode'

urlpatterns = [
    # url是经常变化的，如果在代码中写死，可能会经常改代码
    # 给url取个名字'name=xxx'，以后使用url的时候就使用它的名字进行反转就可以了reverse
    # 若多个app中出现同名url，使用应用命名空间可解决冲突问题
    path('discovery/', views.discovery_view, name='discover'),
]
