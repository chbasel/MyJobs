from datetime import datetime, timedelta
import operator
import pytz

from django import http
from django.core.urlresolvers import reverse
from django.utils.timezone import activate
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.shortcuts import redirect

from impersonate.middleware import ImpersonateMiddleware

from myjobs.models import User, SecondPartyAccessRequest
from postajob.models import SitePackage
from seo.models import SeoSite, SeoSiteRedirect, SeoSiteFacet
import version


if settings.NEW_RELIC_TRACKING:
    try:
        import newrelic.agent
    except ImportError:
        pass


class PasswordChangeRedirectMiddleware:
    """
    Redirects a user to the password change form if several conditions are met:
    - A user is logged in
    - That user's password_change flag is set to True
    - The user is not trying to log out,
        change passwords, or activate an account

    Returns a 403 status code if the request is ajax and the request dict
    contains the 'next' key (i.e. no user is logged in, a privileged
    page was left open, and an unauthorized user tries to access something
    that they shouldn't)
    """
    def process_request(self, request):
        if request.user.is_authenticated():
            urls = [reverse('read'),
                    reverse('edit_account'),
                    reverse('auth_logout'),
                    reverse('registration_activate', args=['a'])[0:-2]]
            url_matches = reduce(operator.or_,
                                 [request.path.startswith(url)
                                  for url in urls])

            if (not url_matches and request.user.password_change):
                return http.HttpResponseRedirect(reverse('edit_account')
                                                 + '#as-password')

        elif request.is_ajax() and bool(request.GET.get('next', request.POST.get('next'))):
            return http.HttpResponse(status=403)


class NewRelic(object):
    """
    Manages New Relic tracking.

    """
    def process_response(self, request, response):
        newrelic.agent.add_custom_parameter('url', request.META['HTTP_HOST'])
        if hasattr(request, 'user'):
            newrelic.agent.add_custom_parameter('user_id', request.user.id)
        else:
            newrelic.agent.add_custom_parameter('user_id', 'anonymous')
        return response

    def process_request(self, request):
        newrelic.agent.add_custom_parameter('url', request.META['HTTP_HOST'])
        if hasattr(request, 'user'):
            newrelic.agent.add_custom_parameter('user_id', request.user.id)
        else:
            newrelic.agent.add_custom_parameter('user_id', 'anonymous')


class CompactP3PMiddleware(object):
    """
    Adds a compact privacy policy to site headers

    """
    def process_response(self, request, response):
        response['P3P'] = 'CP="ALL DSP COR CURa IND PHY UNR"'
        return response


class TimezoneMiddleware(object):
    """
    Activates the user-selected timezone.

    """
    def process_request(self, request):
        if hasattr(request, 'user') and not request.user.is_anonymous():
            try:
                activate(pytz.timezone(request.user.timezone))
            except Exception:
                activate(pytz.timezone('America/New_York'))


class SiteRedirectMiddleware:
    def process_request(self, request):
        """
        Find out if we need to redirect to a different url.

        There's 3 cases we need to handle:
        1. A site exists and has a redirect.
        2. A site exists but has no redirect.
        3. The site doesn't exist at all.

        NOTE: this middleware should probably come first, as if we're going
              to redirect, why go thru any other unneeded processing

        """
        host = request.get_host()
        try:
            ss = SeoSiteRedirect.objects. \
                select_related('seosite__domain').get(redirect_url=host)
            redirect_host = ss.seosite.domain
            uri = request.path
            redirect_url = 'http://%s%s' % (redirect_host, uri)
            return redirect(redirect_url, permanent=True)
        except SeoSiteRedirect.DoesNotExist:
            return


class MultiHostMiddleware:
    def process_request(self, request):
        """
        get the host name
        see if we have the settings for the site cached
            - if so, load those
            - if not, grab them from that database
                - store them in cache

        """
        host = None

        # Allow for specifying a domain to use as the current site rather
        # than using the site that matches the current domain.
        # Intended use is for testing specific Sites/Configurations
        # in QC/Staging.
        if request.user.is_authenticated() and request.user.is_staff:
            host = request.GET.get('domain', request.POST.get("domain"))
            # If a user is domain switching, assume they really do know
            # where they want to go.
            setattr(settings, 'WILDCARD_REDIRECT', False)

        if host is None:
            host = request.get_host()

        # get rid of any possible port number that comes thru on the host
        # examples:    localhost:80,
        #             127.0.0.1:8000,
        #             find.ibm.jobs:80
        host = host.split(":")[0]
        site_cache_key = '%s:SeoSite' % host
        MINUTES_TO_CACHE = getattr(settings, 'MINUTES_TO_CACHE', 120)
        ## REMINDER: make domain a unique field on site model
        # see if the cache has it
        my_site = cache.get(site_cache_key)
        if not my_site:
            # DO NOT add filters to prefetched objects. Use only with .all()
            sites = SeoSite.objects.select_related('group',
                                                   'microsite_carousel',
                                                   'view_sources',
                                                   ).prefetch_related('billboard_images',
                                                                      'business_units',
                                                                      'featured_companies',
                                                                      'site_tags',
                                                                      'google_analytics',
                                                                      'queryredirect_set')
            # the cache didn't have it, so lets get it and set the cache
            try:
                my_site = sites.get(domain=host)
            except Site.MultipleObjectsReturned:
                my_site = sites.filter(domain=host)[:1][0]
            except Site.DoesNotExist:
                my_site = sites.get(id=1)
            cache.set(site_cache_key, my_site, MINUTES_TO_CACHE*60)
        settings.SITE = my_site
        my_buids = [bu.id for bu in my_site.business_units.all()]
        settings.SITE_ID = my_site.id
        settings.SITE_NAME = my_site.name
        settings.SITE_BUIDS = my_buids
        settings.SITE_TAGS = [tag.site_tag for tag in my_site.site_tags.all()]
        # version information
        settings.VERSION = version.marketing_version
        settings.BUILD = version.build_calculated
        settings.FULL_VERSION = version.release_number

        # Place variables that need a non blank default value here
        if my_site.site_title:  # title defaults to site name
            settings.SITE_TITLE = my_site.site_title
        else:
            settings.SITE_TITLE = my_site.name
        if my_site.site_heading:  # heading defaults to site name
            settings.SITE_HEADING = my_site.site_heading
        else:
            settings.SITE_HEADING = my_site.name
        if my_site.site_description:
            settings.SITE_DESCRIPTION = my_site.site_description
        else:
            settings.SITE_DESCRIPTION = None

        # Default variable loading. Assigns empty string as default
        site_flags = {
            'ats_source_codes': 'ATS_SOURCE_CODES',
            'google_analytics_campaigns': 'GA_CAMPAIGN',
            'special_commitments': 'COMMITMENTS',
            'view_sources': 'VIEW_SOURCE'
        }

        for k, v in site_flags.items():
            attr = getattr(my_site, k)
            if attr:
                setattr(settings, v, attr)
            else:
                setattr(settings, v, '')

        site_facets = SeoSiteFacet.objects.filter(seosite=my_site)
        site_facets = site_facets.select_related('customfacet')

        settings.CACHE_MIDDLEWARE_KEY_PREFIX = "%s" % my_site.domain

        default = SeoSiteFacet.DEFAULT
        default_site_facets = site_facets.filter(facet_type=default)
        settings.DEFAULT_FACET = custom_facets_ops_groups(default_site_facets)

        featured = SeoSiteFacet.FEATURED
        featured_site_facets = site_facets.filter(facet_type=featured)
        settings.FEATURED_FACET = custom_facets_ops_groups(featured_site_facets)

        standard = SeoSiteFacet.STANDARD
        standard_site_facets = site_facets.filter(facet_type=standard)
        settings.STANDARD_FACET = custom_facets_ops_groups(standard_site_facets)

        packages = SitePackage.objects.filter(sites=my_site)
        settings.SITE_PACKAGES = [int(site_package.pk)
                                  for site_package in packages]


def custom_facets_ops_groups(site_facets):
    """
    Returns a list of custom facets with boolean_operation attributes set
    from site facets

    """
    custom_facets = []
    for site_facet in site_facets:
        custom_facet = site_facet.customfacet
        setattr(custom_facet, 'boolean_operation', site_facet.boolean_operation)
        setattr(custom_facet, 'facet_group', site_facet.facet_group)
        custom_facets.append(custom_facet)
    return custom_facets


def filter_custom_facets_by_production_status(custom_facets):
    return [facet for facet in custom_facets if facet.show_production]


class RedirectOverrideMiddleware(object):
    """
    Determines if we need to redirect based on the current path, any query
    strings, and any entries in the QueryRedirect table for the current domain.
    """
    def process_request(self, request):
        if not settings.SITE.queryredirect_set.all():
            return
        paths = [request.path,
                 (request.path[:-1] if request.path.endswith('/')
                  else request.path + '/')]
        param_names = ['q', 'location', 'moc']
        url_params = [param for param in param_names
                      if param + '=' in request.META['QUERY_STRING'].lower()]
        redirects = settings.SITE.queryredirect_set.filter(
            old_path__in=paths,
            **{param + '__isnull': param not in url_params
               for param in param_names})
        choice = None
        for r in redirects:
            # params will, over the following three lines, eventually hold all
            # defined query parameters for the current QueryRedirect object,
            # in the form of a list of tuples of (parameter, value).
            params = [getattr(r, param).value
                      if hasattr(r, param) else ''
                      for param in param_names]
            params = zip(param_names, params)
            params = filter((lambda x: x[1] != ''), params)
            if len(params) > 0:
                # This QueryRedirect has query params that we need to check
                for param, value in params:
                    # Determine if the current value is multi-valued and
                    # normalize it to a list regardless
                    values = value.split('|')
                    # Turn the previous tuple into a list of param=value strings
                    test_params = ['='.join([param, x]) for x in values]
                    if not any(test_param.lower()
                               in request.META['QUERY_STRING'].lower()
                               for test_param in test_params):
                        break
                else:
                    choice = r
                    break
            else:
                # This QueryRedirect has no query params to check; it must be
                # the one we want.
                choice = r
                break

        if choice:
            return redirect(choice.new_path, permanent=True)


class ImpersonateTimeoutMiddleware(ImpersonateMiddleware):
    """
    Wraps ImpersonateMiddleware with a check for non-expired access requests
    """
    def process_request(self, request):
        request.user.is_impersonate = False
        request.impersonator = None

        # This conditional is nearly identical to the one in
        # ImpersonateMiddleware. We had to add the request.path check as
        # we would otherwise be in a redirect loop.
        if (request.user.is_authenticated()
                and '_impersonate' in request.session
                and request.path != reverse('impersonate-stop')):
            user_id = request.session['_impersonate']
            if isinstance(user_id, User):
                user_id = user_id.id

            # We should only allow impersonation if there is an active
            # SecondPartyAccessRequest that has been in use for less than
            # two hours.
            now = datetime.now()
            started = now - timedelta(hours=2)
            access_request = SecondPartyAccessRequest.objects.filter(
                second_party=request.user, account_owner__id=user_id,
                session_started__range=(started, now),
                session_finished__isnull=True)
            if access_request:
                return super(ImpersonateTimeoutMiddleware,
                             self).process_request(request)
            else:
                return redirect(reverse('impersonate-stop'))


class SessionTimeMiddleware(object):
    """
    Adds a cookie that tracks the amount of time remaining in a session.

    This allows us to redirect a user to the login page via JavaScript
    if their session expires.

    """
    def process_response(self, request, response):
        session_expiry_age = 0

        if hasattr(request, 'user') and request.user.is_authenticated():
            session_expiry_age = request.session.get_expiry_age()

        if session_expiry_age and session_expiry_age > 0:
            response.set_cookie('exp', str(session_expiry_age),
                                expires=session_expiry_age)

        return response
