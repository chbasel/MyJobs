from django.conf.urls import url, patterns, include

# API URLs
api_patterns = patterns(
    'analytics.api',
    url(r'^available-reports', 'get_available_analytics',
        name='available_reports'),
    url(r'^report-info', 'get_report_info',
        name='get_report_info'),
    url(r'^views-week', 'views_last_7_days', name='views_last_7_days'),
    url(r'^activity-week', 'activity_last_7_days',
        name='activity_last_7_days'),
    url(r'^campaign-percent', 'campaign_percentages',
        name='campaign_percentages'),
    url(r'^dynamic', 'dynamic_chart', name='dynamic_chart'),
)

# View URLs

view_patterns = patterns(
    'analytics.views',
    url(r'^main', 'analytics_main', name='analytics_main'),
)


urlpatterns = patterns(
    '',
    url(r'^api/', include(api_patterns)),
    url(r'^view/', include(view_patterns)),
)
