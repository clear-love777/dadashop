from django.conf.urls import url

from ntoken import views

urlpatterns=[
    url(r"^$",views.token_view)
]