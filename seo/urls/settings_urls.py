from django.conf.urls import patterns, url

from seo.views import settings_views

urlpatterns = patterns(
    'seo.views.settings_views',

    # SeoSites Domain
    url(r'^site/domain',
        settings_views.EmailDomainFormView.as_view(),
        name='seosites_settings_email_domain_edit'),
    url(r'^view_sources', 'get_view_sources', name='get_view_sources'),
)
