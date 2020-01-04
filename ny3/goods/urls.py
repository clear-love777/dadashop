from django.conf.urls import url

from goods import views

urlpatterns=[
    url(r"^/index$",views.GoodsIndexView.as_view()),
    url(r"^/detail/(?P<sku_id>\w+)$",views.GoodsDetailView.as_view()),
    url(r"^/sku$",views.GoodsDetailView.as_view())
]