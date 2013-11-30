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
	 (r'^rtt_json/(?P<device>.+)/(?P<days>.+)/(?P<dstip>.+)', 'networkdashboard.summary.views.rtt_json'),
	 (r'^lmrtt_json/(?P<device>.+)/(?P<days>.+)', 'networkdashboard.summary.views.lmrtt_json'),
	 (r'^bitrate_json/(?P<device>.+)/(?P<days>.+)/(?P<direction>.+)/(?P<multi>.+)', 'networkdashboard.summary.views.bitrate_json'),
	 (r'^compare_by_city/(?P<city>.+)/(?P<country>.+)', 'networkdashboard.summary.views.compare_by_city'),
	 (r'^compare_by_country/(?P<country>.+)', 'networkdashboard.summary.views.compare_by_country'),
	 (r'^compare_by_isp/(?P<isp>.+)/(?P<country>.+)', 'networkdashboard.summary.views.compare_by_isp'),
	 (r'^compare_by_isp_and_city/(?P<isp>.+)/(?P<city>.+)', 'networkdashboard.summary.views.compare_by_isp_and_city'),
	 (r'^compare_line_bitrate_by_city/', 'networkdashboard.summary.views.compare_line_bitrate_by_city'),
	 (r'^compare_bar_bitrate_by_city/', 'networkdashboard.summary.views.compare_bar_bitrate_by_city'),
	 (r'^compare_bitrate_by_country/', 'networkdashboard.summary.views.compare_bitrate_by_country'),
	 (r'^compare_line_bitrate_by_isp/', 'networkdashboard.summary.views.compare_line_bitrate_by_isp'),
	 (r'^compare_bar_bitrate_by_isp/', 'networkdashboard.summary.views.compare_bar_bitrate_by_isp'),
	 (r'^compare_line_lmrtt_by_city/', 'networkdashboard.summary.views.compare_line_lmrtt_by_city'),
	 (r'^compare_bar_lmrtt_by_city/', 'networkdashboard.summary.views.compare_bar_lmrtt_by_city'),
	 (r'^compare_lmrtt_by_country/', 'networkdashboard.summary.views.compare_lmrtt_by_country'),
	 (r'^compare_line_lmrtt_by_isp/', 'networkdashboard.summary.views.compare_line_lmrtt_by_isp'),
	 (r'^compare_bar_lmrtt_by_isp/', 'networkdashboard.summary.views.compare_bar_lmrtt_by_isp'),
	 (r'^compare_line_rtt_by_city/', 'networkdashboard.summary.views.compare_line_rtt_by_city'),
	 (r'^compare_bar_rtt_by_city/', 'networkdashboard.summary.views.compare_bar_rtt_by_city'),
	 (r'^compare_rtt_by_country/', 'networkdashboard.summary.views.compare_rtt_by_country'),
	 (r'^compare_line_rtt_by_isp/', 'networkdashboard.summary.views.compare_line_rtt_by_isp'),
	 (r'^compare_bar_rtt_by_isp/', 'networkdashboard.summary.views.compare_bar_rtt_by_isp'),
     (r'^device', 'networkdashboard.summary.views.device_summary'),
     (r'^get_coordinates', 'networkdashboard.summary.views.get_coordinates'),
     (r'^display_device/(?P<hash>.+)/(?P<tab>.+)/(?P<start>.+)/(?P<end>.+)', 'networkdashboard.summary.views.shared_device_summary'),
     (r'^edit_device_page/(?P<device>\w+)', 'networkdashboard.summary.views.edit_device_page'),
     (r'^get_location/(?P<hash>\w+)', 'networkdashboard.summary.views.get_location'),
     (r'^line_rtt', 'networkdashboard.summary.views.linegraph_rtt'),
     (r'^line_bitrate/', 'networkdashboard.summary.views.linegraph_bitrate'),
     (r'^line_lmrtt/', 'networkdashboard.summary.views.linegraph_lmrtt'),
     (r'^line_shaperate/', 'networkdashboard.summary.views.linegraph_shaperate'),
	 (r'^line_unload/', 'networkdashboard.summary.views.linegraph_unload'),
     (r'^static/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.MEDIA_ROOT}),
     (r'^countries_vis/get_countries_vis_data/', 'networkdashboard.summary.views.get_countries_vis_data'),
     (r'^countries_vis/', 'networkdashboard.summary.views.countries_vis')
)
