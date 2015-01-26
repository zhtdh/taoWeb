__author__ = 'zhangtao'
#coding:utf-8
from django import VERSION
from django.conf.urls import patterns, url

from App.ueditor.views import get_ueditor_controller

urlpatterns = patterns('',
    url(r'controller/$',get_ueditor_controller)
)