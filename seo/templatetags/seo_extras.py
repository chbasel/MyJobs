import datetime
import itertools
from pysolr import safe_urlencode
import random
import re
from slugify import slugify
import unicodedata
from bs4 import BeautifulSoup
import markdown2
from urlparse import urlparse, urlunparse, parse_qsl
from urllib import urlencode

from django import template
from django.conf import settings
from django.core.cache import cache
from django.template.defaultfilters import stringfilter
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince
from django.utils.translation import ugettext
from django.http import QueryDict

from seo.models import CustomPage, Company, GoogleAnalytics, SiteTag
from universal.helpers import get_object_or_none, update_url_param


register = template.Library()


@register.inclusion_tag('includes/newrelic_browser_monitoring.html')
def newrelic_browser_monitoring():
    # Only use the script tag on 1% of page loads.
    return {'newrelic_monitoring_enabled': random.random() < 0.01 }


@register.filter
@stringfilter
def case_insensitive_cut(value, args):
    args = re.compile(re.escape(args), re.IGNORECASE)
    return args.sub('', value)


@register.filter
@stringfilter
def replace(value, args):
    args = args.split('~')
    return value.replace(args[0], args[1])


@register.filter
@stringfilter
def append(value, arg):
    if value != '':
        return value + arg
    else:
        return ''


@register.filter
@stringfilter
def smart_truncate(content, length=32, suffix='...'):
    if isinstance(content, unicode):
        # reduce length by 1 for each wide char
        for c in content:
            if unicodedata.east_asian_width(c) == "W":
                length -= 1
    if len(content) <= length:
        return content
    else:
        return content[:length]+suffix


@register.filter
@stringfilter
def build_rss_link(val):
    val = escape(val)
    split = val.rsplit('?', 1)
    split[0] = split[0].rstrip('/') + '/feed/rss'
    return '?'.join(split)


@register.filter
@stringfilter
def facet_text(val):
    """
    This filter will take the passed in value of the form:
        url::text
    and parse out the text value and return that.
    """
    pieces = val.split("::")
    return pieces[1]


@register.filter
@stringfilter
def facet_url(val):
    """
    This filter will take the passed in value of the form:
        url::text
    and parse out the url value and return that.
    """
    pieces = val.split("::")
    return pieces[0]


@register.tag
def calculate_microsite_tags(parser, token):
    """
    This is a custom template tag used to calculate the opening and
    closing of columns for the microsite depending on a variable number
    of rows. An array is passed to it as a context variable to calculate
    the opening/closing of html tags to form the columns of the microsite
    carousel, processed by the VariableCycleNode

    """
    try:
        tag_name, cycle_string = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" %
                                           token.contents.split()[0])
    return VariableCycleNode(parser.compile_filter(cycle_string))


class VariableCycleNode(template.defaulttags.CycleNode):
    """
    This is a custom template code that can be used to cycle values from
    an array that is passed into the filter tag from a context variable

    """
    def __init__(self, cyclevars, variable_name=None):
        self.cyclevars = cyclevars
        self.variable_name = variable_name

    def render(self, context):
        my_vars = self.cyclevars.resolve(context)
        if self not in context.render_context:
            context.render_context[self] = itertools.cycle(my_vars)
        cycle_iter = context.render_context[self]
        value = cycle_iter.next()
        if self.variable_name:
            context[self.variable_name] = value
        return value


@register.filter
@stringfilter
def multiply_value(value, arg):
    if value != '':
        return int(value) * int(arg)
    else:
        return ''


def get_params(request):
    """
    Given a request, gets all of the parameters that should be persist onto
    other pages for analytics purposes.

    :param request: A Django request object representing the current request.
    :return: A dictionary of the params that should be persisted. Formatted:
             {'param': 'value', ...}
    """
    params = {}
    params_to_persist = [
        'de_n', 'de_m', 'de_t', 'de_o', 'de_c', 'utm_source', 'utm_medium',
        'utm_term', 'utm_content', 'utm_campaign'
    ]
    # We store some of the params in cookies across the site, but we don't
    # always us the parameter as the cookie name. This maps cookie name =>
    # querystring parameter
    cookie_field_mappings = {
        'external_utm_campaign': 'utm_campaign',
        'external_utm_medium': 'utm_medium',
        'external_utm_content': 'utm_content',
        'external_utm_source': 'utm_source',
        'external_utm_term': 'utm_term',
    }
    url = request.build_absolute_uri()
    url = urlparse(url)

    for cookie_name, param in cookie_field_mappings.iteritems():
        value = request.COOKIES.get(cookie_name, None)
        # NOTE: Right now there's no check that the param
        # is in params_to_persist because at this time it always will be.
        # If the options in cookie_field_mappings ever change, or the
        # desired params_to_persist ever change, that check will need added.
        if value:
            params[param] = value

    current_params = dict(parse_qsl(url.query))

    for param, value in current_params.iteritems():
        if param in params_to_persist:
            # Blindly update params with the new value, allowing the current
            # url parameters to overwrite the ones taken from the cookie,
            # since the current url is more reliable.
            params[param] = value

    return params


@register.simple_tag(takes_context=True)
def joblist_url(context, job):
    params = {}

    request = context.get('request')
    if request:
        params = get_params(request)

    loc_slug = slugify(job.location)
    title_slug = slugify(job.title)

    path = '/%s/%s/%s/job/' % (loc_slug, title_slug, job.guid)
    querystring = urlencode(params)

    return urlunparse(('', '', path, '', querystring, ''))


@register.filter
def merge_snippets(hl):
    snippets = hl['text']
    return ' ... '.join([i for i in snippets]) + ' ... '


@register.filter
def timedelta(value, arg=None):
    if not value:
        return ''

    if arg:
        default = arg
    else:
        default = datetime.datetime.now()

    ts = timesince(default, value)

    if value > default:
        retval = "in %s" % ts
    else:
        retval = "%s ago" % ts

    return retval


@register.simple_tag
def append_search_querystring(request, feed_path):
    if request.path == '/search':
        qs = "?%s" % safe_urlencode(request.GET.items())
    else:
        qs = ""

    return feed_path+qs


@register.assignment_tag(takes_context=True)
def custom_page_navigation(context):
    cache_key = '%s:custom_page_links' % context['request'].get_host()
    timeout = 60 * settings.MINUTES_TO_CACHE
    html = cache.get(cache_key)

    if html is None:
        links = CustomPage.objects.filter(
            sites=settings.SITE_ID).values_list('url', 'title')
        html = "".join(["<a href='%s'>%s</a>" % (url, title)
                        for (url, title) in links])
        cache.set(cache_key, html, timeout)
    return html


@register.inclusion_tag('logo-carousel.html', takes_context=True)
def logo_carousel(context):
    if context['company_images'] is not None:
        num_of_cos = len(context['company_images'])
    else:
        num_of_cos = 0
    displayed = context['site_config'].browse_company_show and bool(num_of_cos)
    return {
        'displayed': displayed,
        'num_of_cos': num_of_cos
    }


@register.inclusion_tag('filter-carousel.html', takes_context=True)
def filter_carousel(context):
    widgets = context['widgets']
    # A set of widgets will always be returned, but they may not have any items.
    has_widgets = False
    for each in widgets:
        if each.items:
            has_widgets = True
            break
    return {'widgets': widgets, 'has_widgets': has_widgets}


@register.filter
@stringfilter
def to_slug(co_slab):
    return co_slab.split("::")[0].split("/")[0]


@register.filter
def compare(a, b):
    return a == b


@register.filter
@stringfilter
def highlight_solr(description):
    html = markdown2.markdown(description, safe_mode="replace")
    text = escape(BeautifulSoup(html).text)
    highlighted = text.replace("###{{{###", "<b>").replace("###}}}###", "</b>")
    return mark_safe(highlighted)


@register.assignment_tag(takes_context=True)
def flatpage_site_heading(context):
    """
    Returns site heading for pages where the context variable isn't loaded

    """
    return context.get('site_heading', settings.SITE_HEADING)


@register.assignment_tag(takes_context=True)
def flatpage_site_tags(context):
    """
    Returns site tags for pages where the context variable isn't loaded

    """
    return context.get('site_tags', settings.SITE_TAGS)


@register.assignment_tag(takes_context=True)
def flatpage_site_description(context):
    """
    Returns site description for pages where the context variable isn't loaded

     """
    return context.get('site_description', settings.SITE_DESCRIPTION)


@register.assignment_tag(takes_context=True)
def flatpage_site_title(context, *args, **kwargs):
    """
    Returns site title for pages where the context variable isn't loaded

    CustomPage calls flatpage_site_title with an extra blank string as an
    argument, args=('', ''), so we're catching args and kwargs to to
    prevent an error. There are no obvious places we're calling
    flatpage_site_title or site_title with an extra space, so this may be
    related to the "as" renaming we do in seo_base.html.

    """
    return context.get('site_title', settings.SITE_TITLE)


def get_ga_context():
    """
    rebuilds the google analytics template for flatpages by reconstructing
    the context variable manually

    Inputs:
    none

    Returns:
    ga.html and footer.html rendered with manual context variable.

    """
    site_id = settings.SITE_ID
    ga = GoogleAnalytics.objects.filter(seosite=site_id)
    view_source = settings.VIEW_SOURCE
    build_num = settings.BUILD
    return {
        'google_analytics': ga,
        'view_source': view_source,
        "build_num": build_num
    }


@register.assignment_tag
def all_site_tags():
    tags = SiteTag.objects.exclude(tag_navigation=False).values_list('site_tag',
                                                                     flat=True)
    return tags


@register.inclusion_tag('ga.html', takes_context=False)
def flatpage_ga():
    return get_ga_context()


@register.inclusion_tag('wide_footer.html', takes_context=False)
def flatpage_footer_ga():
    return get_ga_context()


@register.simple_tag
def view_all_jobs_label(view_all_jobs_detail):
    """
    Reads the view_all_jobs_detail config setting, and builds a new link label
    from the site title if enabled. This tag does not impact display of the
    jobs counts.

    Inputs:
    :view_all_jobs_detail: Boolean, set to True to include site title
                           information in label
    Returns:
    :label: Text to display in the search footer.

    """
    label = ugettext("View All Jobs")
    # time to build the new string. This assumes each word is capitalized
    if view_all_jobs_detail:
        cos = settings.SITE.business_units.all()
        if cos:
            # strip "Jobs" from the end
            label = settings.SITE_TITLE.replace("Jobs", "")
            for company in cos:
                # strip any phrases that match the company title. This will
                # leave only phrases from the title that reflect the desired
                # facet info
                if company.title is not None:
                    label = label.replace(company.title, "")
            # assemble the final string and then defrag any spaces (for testing)
            label = "View All %s Jobs" % label
            label = ugettext(re.sub(r"([ ])+", " ", label))

    return label


@register.simple_tag
def build_title(site_title, search_q, location_q, company, heading):
    """
    Build title and metatag title based on search queries and other filters.

    Returns:
    :title:     Returns a string that is the title for the page.
    """
    title = site_title + " - "

    if company:
        title += "%s %s" % (company, "Careers - ")

    if search_q == "\*":
        pass
    elif search_q and heading == "Jobs":
        title += search_q.title() + " "
    elif search_q:
        title += search_q.title() + " - "

    if not heading:
        title += "All Jobs "
    else:
        title += heading + " "

    if location_q == "\*":
        pass
    elif location_q and not location_q in title:
        title += "in " + location_q

    return escape(title)


@register.filter
def make_pixel_qs(request, job=None):
    """
    Constructs a query string that will be appended onto a url pointing at
    the My.jobs tracking pixel. This qs should contain all of the information
    we want to track about this request.

    Inputs:
    :request: HttpRequest object for this request
    :job: the current job, if this is a job detail page

    Returns:
    :safe_qs: Encoded, and marked safe query string
    """
    current_site = settings.SITE
    commitments = current_site.special_commitments.all().values_list('commit',
                                                                     flat=True)

    vs = settings.VIEW_SOURCE
    if vs:
        vs = vs.view_source
    else:
        vs = 88
    qd = QueryDict('', mutable=True)
    qd.setlist('st', settings.SITE_TAGS)
    qd.setlist('sc', commitments)
    qs = {'d': current_site.domain,
          'jvs': vs}
    if request.path == '/':
        qs['pc'] = 'home'
    elif job:
        qs['pc'] = 'listing'
        qs['jvb'] = job.buid if job.buid else 0
        qs['jvg'] = job.guid
        qs['jvt'] = job.title_exact
        qs['jvc'] = job.company_exact
        qs['jvl'] = job.location_exact
        try:
            company = Company.objects.get(name=job.company_exact)
            qs['jvcd'] = company.canonical_microsite
        except Company.DoesNotExist:
            pass
    else:
        qs['pc'] = 'results'
        qs['sl'] = request.GET.get('location', request.POST.get('location', ''))
        qs['sq'] = request.GET.get('q', request.POST.get('q', ''))
    qd.update(qs)
    safe_qs = mark_safe(qd.urlencode())
    return safe_qs


@register.simple_tag(takes_context=True)
def url_for_sort_field(context, field):
    current_url = context['request'].build_absolute_uri()
    new_url = update_url_param(current_url, 'sort', field)
    return mark_safe('<a href=%s rel="nofollow">Sort by %s</a>' %
                     (new_url, field.title()))


@register.assignment_tag
def get_custom_page(flatpage):
    return get_object_or_none(CustomPage, pk=flatpage.pk)


@register.assignment_tag(takes_context=True)
def is_special_case(context, job):
    return ((job.country_short or '').lower() in ['usa', 'can']
            and bool(job.state))
