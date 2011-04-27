from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^dashboard/', include('dashboard.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/', include(admin.site.urls)),

    # site URLs
     (r'^$', 'dashboard.summary.views.index'),
     (r'^devices/', 'dashboard.summary.views.showdevices'),
     (r'^device/(?P<device>\w+)', 'dashboard.summary.views.devicesummary'),
     (r'^data/$', 'dashboard.summary.views.scatter_data'),
     (r'^static/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.MEDIA_ROOT})
)

