# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views
app_name = 'ipdhcp'

urlpatterns = [
    url(r'^$', views.dhcps, name='dhcps'),
]