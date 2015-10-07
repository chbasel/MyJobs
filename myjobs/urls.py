from django.conf.urls import patterns, url, include
from django.views.generic import RedirectView

from myjobs.views import About, Privacy, Terms
from myjobs.child_dashboard import child_dashboard

accountpatterns = patterns('myjobs.views',
    url(r'^edit/$', 'edit_account', name='edit_account'),
    url(r'^delete$', 'delete_account', name='delete_account'),
    url(r'^disable$', 'disable_account', name='disable_account'),
    url(r'^$',
        RedirectView.as_view(url='/account/edit/')),
)

urlpatterns = patterns(
    'myjobs.views',

    url(r'^$', 'home', name='home'),
    url(r'^login$',
        RedirectView.as_view(url='/')),
    # Url is duplicated so that we can also easily refer to it as the
    # login url. This might mess with things if you try to resolve a url
    # and use url_name, since it could be either home or login.
    url(r'^$', 'home', name='login'),

    url(r'^about/$', About.as_view(), name='about'),
    url(r'^privacy/$', Privacy.as_view(), name='privacy'),
    url(r'^terms/$', Terms.as_view(), name='terms'),
    url(r'^contact/$', 'contact', name='contact'),
    url(r'^contact-faq', 'contact_faq', name='contact_faq'),
    url(r'^batch$', 'batch_message_digest', name='batch_message_digest'),
    url(r'^unsubscribe/$', 'unsubscribe_all', name='unsubscribe_all'),
    url(r'^account/', include(accountpatterns)),
    url(r'^send/$', 'continue_sending_mail', name='continue_sending_mail'),
    url(r'^toolbar/$', 'toolbar', name='toolbar'),
    url(r'^cas/$', 'cas', name='cas'),
    url(r'^topbar/$', 'topbar', name='topbar'),
    url(r'^child-dashboard/$', child_dashboard, name='child_dashboard'),
)
