from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
     url(r'^$', 'index.views.domian_list'),
     url(r'^record/list/(\d*)', 'index.views.record_list'),
     url(r'^domain/info/(\d*)', 'index.views.domain_info'),
     url(r'^domain/add', 'index.views.domain_add'),
     url(r'^domain/remove/(\d*)', 'index.views.domain_remove'),
     url(r'^record/add/(\d*)', 'index.views.record_add'),
     url(r'^record/remove/(\d*)/(\d*)', 'index.views.record_remove'),
    # url(r'^dnspod/', include('dnspod.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
