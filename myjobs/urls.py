from django.conf.urls import patterns, url, include
from django.views.generic import RedirectView

from myjobs.views import About, Privacy, Terms

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
    url(r'^manage-users/$', 'manage_users', name='manage_users'),
    url(r'^manage-users/api/roles/$', 'api_roles', name='api_roles'),
    url(r'^manage-users/api/roles/(?P<role_id>[0-9]+)/$', 'api_roles', name='api_roles'),




    url(r'^manage-users/api/activities$', 'api_activities', name='api_activities'),
)
