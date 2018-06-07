from django.conf.urls import url

from . import views

urlpatterns = [
#    url(r'', views.index),
    url(r'^logs/(?P<user>.+)/(?P<room>.+)/(?P<namespace>.+)$', views.logs),
]
