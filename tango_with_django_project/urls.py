from django.conf.urls import patterns, include, url

from django.contrib import admin

from django.conf.urls import patterns, url
from rango import views
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tango_with_django_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^rango/', include('rango.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    url(r'^$',views.index,name='index'),
    # url(r'^add_category/$', views.add_category, name='add_category'), # NEW MAPPING!
    #url(r'^rango/category/(?P<category_name_url>\w+)/$', views.category, name='category'),  # New!
)

# At the top of your urls.py file, add the following line:
# UNDERNEATH your urlpatterns definition, add the following two lines:
if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        (r'media/(?P<path>.*)', 'serve', {'document_root':settings.MEDIA_ROOT}),
    )