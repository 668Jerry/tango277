from django.conf.urls import patterns, url
from rango import views

from django.conf.urls import patterns, include, url

from django.contrib import admin

from django.conf.urls import patterns, url
from rango import views
from django.conf import settings

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    # url(r'^about/$', views.about, name='about'),
    url(r'^add_category/$', views.add_category, name='add_category'), # NEW MAPPING!
    url(r'^category/(?P<category_name_url>\w+)/$', views.category, name='category'),  # New!
    )