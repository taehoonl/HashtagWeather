from django.conf.urls import patterns, include, url

from django.contrib import admin

from website.views import Views

admin.autodiscover()

views = Views()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', views.home, name='home'),
    url(r'^weather/$', views.weather, name='weather'),
    url(r'^about/$', views.about, name='about'),
    url(r'^algorithms/$', views.algorithms, name='about'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
