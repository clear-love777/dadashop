from django.conf.urls import url

from carts import views

urlpatterns=[
    url(r"^$",views.test)
]