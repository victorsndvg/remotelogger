from django.conf.urls import url

from . import views

urlpatterns = [
#    url(r'', views.index),
    url(r'^$', views.users, name='users'),
    url(r'^(?P<exchange>[^/]+)$', views.workflows, name='workflows'),
    url(r'^(?P<exchange>[^/]+)/(?P<routing_key>[^/]+)$', views.jobs, name='jobs'),
    url(r'^(?P<exchange>[^/]+)/(?P<routing_key>[^/]+)/(?P<queue>[^/]+)$', views.logs, name='logs'),
]
