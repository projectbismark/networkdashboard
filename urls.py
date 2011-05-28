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
     (r'^activedevices/', 'dashboard.summary.views.showactivedevices'),
     (r'^device/(?P<device>\w+)', 'dashboard.summary.views.devicesummary'),
     (r'^getISP/(?P<device>\w+)', 'dashboard.summary.views.getISP'),
     (r'^getPlan/(?P<device>\w+)', 'dashboard.summary.views.getPlan'),
     (r'^getUl/(?P<device>\w+)', 'dashboard.summary.views.getUl'),
     (r'^getDl/(?P<device>\w+)', 'dashboard.summary.views.getDl'),
     (r'^getLastUpdate/(?P<device>\w+)', 'dashboard.summary.views.getLastUpdate'),
     (r'^getLastUpdateYMD/(?P<device>\w+)', 'dashboard.summary.views.getLastUpdateYMD'),
     (r'^getFirstUpdate/(?P<device>\w+)', 'dashboard.summary.views.getFirstUpdate'),
     (r'^data/(?P<device>\w+)', 'dashboard.summary.views.line_data2'),
     (r'^data_chart/(?P<device>\w+)', 'dashboard.summary.views.cvs_linegraph'),
     (r'^data/', 'dashboard.summary.views.pie_chart'),
     (r'^newuser.html', 'dashboard.summary.views.newuser'),
     (r'^static/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.MEDIA_ROOT})

)

