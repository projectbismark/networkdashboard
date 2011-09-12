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
     (r'^$', 'networkdashboard.summary.views.index'),
     (r'^devices/', 'networkdashboard.summary.views.showdevices'),
     (r'^activedevices/', 'networkdashboard.summary.views.showactivedevices'),
     (r'^device/', 'networkdashboard.summary.views.devicesummary'),
     (r'^editDevicePage/(?P<device>\w+)', 'networkdashboard.summary.views.editDevicePage'),
     (r'^editDevice/(?P<device>\w+)', 'networkdashboard.summary.views.editDevice'),
     (r'^invalidEdit/(?P<device>\w+)', 'networkdashboard.summary.views.invalidEdit'),
     (r'^getISP/(?P<device>\w+)', 'networkdashboard.summary.views.getISP'),
     (r'^getPlan/(?P<device>\w+)', 'networkdashboard.summary.views.getPlan'),
     (r'^getUl/(?P<device>\w+)', 'networkdashboard.summary.views.getUl'),
     (r'^getDl/(?P<device>\w+)', 'networkdashboard.summary.views.getDl'),
     (r'^getLastUpdate/(?P<device>\w+)', 'networkdashboard.summary.views.getLastUpdate'),
     (r'^getLastUpdateYMD/(?P<device>\w+)', 'networkdashboard.summary.views.getLastUpdateYMD'),
     (r'^getFirstUpdate/(?P<device>\w+)', 'networkdashboard.summary.views.getFirstUpdate'),
     (r'^getLocation/(?P<device>\w+)', 'networkdashboard.summary.views.getLocation'),                  
     (r'^data/(?P<device>\w+)', 'networkdashboard.summary.views.line_data2'),
     (r'^data_chart/', 'networkdashboard.summary.views.cvs_linegraph'),
     (r'^data/', 'networkdashboard.summary.views.pie_chart'),
     (r'^newuser.html', 'networkdashboard.summary.views.newuser'),
     (r'^static/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.MEDIA_ROOT})

)

