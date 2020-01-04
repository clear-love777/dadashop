from django.conf.urls import url

from user import views

urlpatterns=[
    #127.0.0.1:8000/v1/users
    url(r"^$",views.user_view),
    url(r"^/activation$",views.active_view),

    #http://127.0.0.1:8000/v1/users/xxx/address
    #get-查询当前用户的所有地址
    #post-给当前用户创建一个地址
    # url(r"^/(?P<username>\w{1,11})/address$",views.address_view),
    url(r"^/(?P<username>\w{1,11})/address$",views.AddressView.as_view()),
    #改 删除
    url(r"^/(?P<username>\w{1,11})/address/(?P<id>\d+)$",views.AddressView.as_view()),
    url(r"^/weibo/authorization$",views.weibo_login),
    #接收前端传来的code,去新浪验证服务器交换 access_token
    url(r"^/weibo/users$",views.WeiBoView.as_view())
]