from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

from redirect.views import myjobs_redirect, home, email_redirect, update_buid

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # Redirect views
    url(r'^(?P<guid>[0-9A-Fa-f]{32})(?P<vsid>\d+)?(?P<debug>\+)?$', home, name='home'),

    # Email Redirect view
    url(r'^email$', email_redirect, name='email_redirect'),

    # View for updating buids
    url(r'^update_buid/$', update_buid, name='update_buid'),

    url(r'^ajax/', include('automation.urls')),

    url(r'^accounts/', include('registration.urls')),
    url(r'^message/', include('mymessages.urls')),

    # Potential www.my.jobs redirect, catches root and anything not caught
    # previously
    url(r'^(?:.*/)?$', myjobs_redirect),
)

urlpatterns += patterns(
    'myjobs.views',
    url(r'^account/edit/$', 'edit_account', name='edit_account'),
    url(r'^account/delete$', 'delete_account', name='delete_account'),
    url(r'^account/disable$', 'disable_account', name='disable_account'),
)

handler404 = 'redirect.views.redirect_404'
handler500 = 'redirect.views.redirect_500'
