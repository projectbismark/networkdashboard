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

#feedback.html?device=231425325

    # site URLs
     (r'^$', 'networkdashboard.summary.views.index'),
     (r'^devices/', 'networkdashboard.summary.views.showdevices'),
     (r'^compare/', 'networkdashboard.summary.views.compare'),
	 (r'^compare_by_city/(?P<city>.+)', 'networkdashboard.summary.views.compare_by_city'),
	 (r'^compare_bitrate/', 'networkdashboard.summary.views.compare_bitrate'),
	 (r'^compare_lmrtt/', 'networkdashboard.summary.views.compare_lmrtt'),
	 (r'^compare_rtt/', 'networkdashboard.summary.views.compare_rtt'),
	 (r'^compare_bitrate_by_city/', 'networkdashboard.summary.views.compare_bitrate_by_city'),
	 (r'^compare_lmrtt_by_city/', 'networkdashboard.summary.views.compare_lmrtt_by_city'),
	 (r'^compare_rtt_by_city/', 'networkdashboard.summary.views.compare_rtt_by_city'),
	 (r'^activedevices/', 'networkdashboard.summary.views.showactivedevices'),
     (r'^device', 'networkdashboard.summary.views.devicesummary'),
     (r'^getCoordinates', 'networkdashboard.summary.views.getCoordinates'),
     (r'^getLatestInfo/', 'networkdashboard.summary.views.getLatestInfo'),
     (r'^getThroughput', 'networkdashboard.summary.views.throughputGraph'),
     (r'^displayDevice/(?P<devicehash>\w+)', 'networkdashboard.summary.views.sharedDeviceSummary'),
     (r'^editDevicePage/(?P<devicehash>\w+)', 'networkdashboard.summary.views.editDevicePage'),
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
     (r'^line_rtt', 'networkdashboard.summary.views.linegraph_rtt'),
     (r'^line_bitrate/', 'networkdashboard.summary.views.linegraph_bitrate'),
     (r'^line_lmrtt/', 'networkdashboard.summary.views.linegraph_lmrtt'),
     (r'^line_shaperate/', 'networkdashboard.summary.views.linegraph_shaperate'),
     (r'^line_passive/', 'networkdashboard.summary.views.linegraph_bytes_hour'),
	 (r'^line_unload/', 'networkdashboard.summary.views.linegraph_unload'),
     (r'^line_passive_port/', 'networkdashboard.summary.views.linegraph_bytes_port_hour'),
     (r'^data/', 'networkdashboard.summary.views.pie_chart'),
     (r'^newuser.html', 'networkdashboard.summary.views.newuser'),
     (r'^feedback.html', 'networkdashboard.summary.views.feedback'),
     (r'^send_feedback/', 'networkdashboard.summary.views.send_feedback'),
     (r'^ip_test/', 'networkdashboard.summary.views.iptest'),
     (r'^static/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.MEDIA_ROOT})

)



