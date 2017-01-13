"""Generic helper functions."""

from copy import copy, deepcopy
from HTMLParser import HTMLParser
from pkgutil import simplegeneric
import re
import urllib
from urlparse import urlparse, urlunparse

from django.db import connection
from django.db.models.loading import get_model
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import EmailMessage
from django.http import QueryDict


def every(x, y):
    """
    Returns True if every element of x is also an element of y.

    :Inputs
    :x: An iterable of hashable values.
    :y: An iterable of elements of the same time as x's elements.

    :Output
    A boolean.

    Example::

        every([1, 2, 3], [1, 2, 3]) => True
        every([1, 2, 3], [2, 3, 4]) => False

    """
    return set(x).issubset(y)


def at_least_one(x, y):
    """
    Returns True if at least one element of x is also an element of y.

    :Inputs
    :x: An iterable of hashable values.
    :y: An iterable of elements of the same time as x's elements.

    :Output
    A boolean.

    Example::

        at_least_one([1, 2, 3], [3, 4, 5]) => True
        at_least_one([1, 2, 3], [4, 5, 6]) => False

    """
    return not set(x).isdisjoint(y)


def update_url_param(url, param, new_val):
    """
    Changes the value for a parameter in a query string. If the parameter
    wasn't already in the query string, it adds it.

    inputs:
    :url: The url containing the query string to be updated.
    :param: The param to be changed.
    :new_val: The value to update the param with.

    outputs:
    The new url.
    """

    url_parts = list(urlparse(url))
    parts = copy(url_parts)
    query = QueryDict(parts[4], mutable=True)
    query[param] = new_val
    parts[4] = query.urlencode()

    return urlunparse(parts)


def build_url(reverse_url, params):
    return '%s?%s' % (reverse_url, urllib.urlencode(params))


def get_int_or_none(string):
    try:
        return int(string)
    except (ValueError, TypeError, UnicodeEncodeError):
        return None


def get_domain(url):
    """
    Attempts to determine the domain from a url with unknown formatting.

    Created because urlparse.urlparse doesn't handle urls with a
    missing protocol very well. Unfortunately this doesn't handle
    anything except no protocol, http, or https at all.

    """
    pattern = '(http://|https://)?([^/]*\.)?(?P<domain>[^/]*\.[^/]*)'
    pattern = re.compile(pattern)
    try:
        return pattern.search(url).groupdict()['domain'].split("/")[0]
    except (AttributeError, KeyError, TypeError):
        return None


def sequence_to_dict(from_):
    """
    Turns a sequence of repeated key, value elements into a dict. The input
    sequence will be truncated at the last odd index.

    This was originally intended to be used to turn faceted fields returned by
    Solr into a dictionary. These lists are of the form
    ['field_name', facet_count]

    Examples:
    list_to_dict([]) => {}
    list_to_dict(['key_1', 1]) => {'key_1': 1}
    list_to_dict(['key_1', 'value_1', 'key_2']) => {'key_1', 'value_1'}

    Inputs:
    :from_: Sequence to be converted

    Output:
        Dictionary created from the input sequence
    """
    return dict(zip(*[iter(from_)] * 2))


def get_company(request):
    """
    Uses the myjobs_company cookie to determine what the current company is.

    """
    if not request.user or not request.user.pk or request.user.is_anonymous():
        return None

    # If settings.SITE is set we're on a microsite, so get the company
    # based on the microsite we're on instead.
    if hasattr(settings, "SITE") and settings.SITE.canonical_company:
        company = settings.SITE.canonical_company

        if company.user_has_access(request.user):
            return company

    # If the current hit is for a non-microsite admin, we don't know what
    # company we should be using; don't guess.
    if request.get_full_path().startswith('/admin/'):
        return None

    company = request.COOKIES.get('myjobs_company')
    if company:
        company = get_object_or_404(get_model('seo', 'company'), pk=company)

        if not company.user_has_access(request.user):
            company = None

    if not company:
        # If the company cookie isn't set, then the user should have
        # only one company, so use that one.

        # This is ugly and is in place only because we didn't update
        # postajob to use roles before the go-live.
        return get_model('seo', 'Company').objects.filter(
            role__user=request.user).first()

    return company


def get_company_or_404(request):
    """ Simple wrapper around get_company that raises Http404 if no valid
        company is found.
    """
    company = get_company(request)

    if not company:
        raise Http404("universal.helpers.get_company_or_404: get_company "
                      "returned None")

    else:
        return company


def get_object_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except (model.DoesNotExist, ValueError):
        return None


def add_pagination(request, object_list, per_page=None):
    """
    Basic Django Pagination -- Pass a list of objects you wish to paginate.
    That listing will be wrapped by the Paginator object then the listing will
    get split into Pages deemed by :objects_per_page:, which is defaulted
    to 10.

    Inputs:
    :object_list:   A list (or Queryset) of an object you wish to paginate.
    :per_page:      Number of objects per page.

    Outputs:
        Returns a Paginator Object. Paginator acts as a wrapper for the object
        list you pass through. The objects and their attributes are still
        accessed the same but has added methods for the paginator and the
        pages that are created.

    """
    try:
        objects_per_page = int(request.GET.get('per_page') or 10)
    except ValueError:
        objects_per_page = 10
    page = request.GET.get('page')
    paginator = Paginator(object_list, per_page or objects_per_page)

    try:
        pagination = paginator.page(page)
    except PageNotAnInteger:
        pagination = paginator.page(1)
    except EmptyPage:
        pagination = paginator.page(paginator.num_pages)

    return pagination


class HTMLTextExtractor(HTMLParser):
    """
    Accepts html input and transforms it into text suitable for a
    text-only email.

    Sample input:
    '''
    <div><p>\tI'm a saved search!   \t</p>\n \n\n \n\n\t
      <a href="foobar.com">\tI can include \tlinks</a></div>
    '''

    Sample output:
    '''
    \n\nI'm a saved search!\n\nfoobar.com\n\nI can include \tlinks
    '''

    Caveats:
    - We remove whitespace at the beginning and end of each line but,
        as demonstrated, we did not remove the tab that was inside the anchor.
    - This started with two endlines. I'm banking on end users not caring but
        it can be fixed if desired.
    """
    # Look on my works, ye Mighty, and despair!
    def __init__(self):
        # HTMLParser is an old-style class. We can't use super().
        HTMLParser.__init__(self)
        self.extracted = []

    @property
    def last_entry(self):
        """
        Grabs the last entry in self.extracted, or an empty string.
        """
        return self.extracted[-1] if self.extracted else ''

    def handle_starttag(self, tag, attrs):
        """
        Extracts hrefs from anchors and inserts them into our output list
        if they are not present.
        """
        if tag == 'a':
            attrs = dict(attrs)
            href = attrs.get('href')
            if href and href not in self.extracted:
                if not self.last_entry.endswith('\n\n'):
                    self.extracted.append('\n\n')
                self.extracted.append(href)

    def handle_data(self, data):
        """
        Manages spacing in our text output.
        """
        is_space = data.isspace()
        last_is_space = self.last_entry.isspace()
        # Weird spacing can cause strange display quirks when a text-only
        # email is interpreted by Gmail, for instance. Futilely try to correct
        # common whitespace issues.
        if not is_space or not last_is_space:
            data = data.strip(' \t')
            if not (self.last_entry.endswith('\n') or
                    data.startswith('\n')):
                self.extracted.append('\n\n')
            self.extracted.append(data)

    def handle_charref(self, number):
        """
        Turns character references into unicode characters.
        """
        codepoint = (int(number[1:], 16)
                     if number[0] in (u'x', u'X')
                     else int(number))
        self.extracted.append(unichr(codepoint))

    def get_text(self):
        """
        Does one final pass of whitespace changes and then returns
        processed text.
        """
        text = u''.join(self.extracted)

        # With a text-only email, newlines are our only formatting option.
        # Removing extraneous spaces here will allow the next statement to
        # be more correct. We also replace special dashes.
        text = text.replace('\n \n', '\n\n').replace(u'\u2013', u'-').replace(
            u'\u2014', u'-')

        # Replace 3+ newlines with two
        text = re.sub("[\n]{3,}", "\n\n", text)

        # Reduce spacing to one space
        text = re.sub("[ ]{2,}", " ", text)
        return text


def extract_text_from_html(contents):
    """
    Use HTMLTextExtractor to extract text from HTML and return the result.
    """
    extractor = HTMLTextExtractor()
    extractor.feed(contents)
    extractor.close()
    return extractor.get_text()


def send_email(email_body, email_type=settings.GENERIC, recipients=None,
               site=None, headers=None, text_only=False, **kwargs):
    recipients = recipients or []

    company_name = 'My.jobs'
    domain = 'my.jobs'

    if site:
        domain = site.email_domain
        try:
            company_name = site.canonical_company.name
        # using object instead of Company to avoid circular imports
        except (ObjectDoesNotExist, AttributeError):
            pass

    kwargs['company_name'] = company_name
    kwargs['domain'] = domain.lower()

    sender = settings.EMAIL_FORMATS[email_type]['address']
    sender = sender.format(**kwargs)

    # Capitalize domain for display purposes.
    kwargs['domain'] = kwargs['domain'].lower()
    subject = settings.EMAIL_FORMATS[email_type]['subject']
    subject = subject.format(**kwargs)

    if text_only:
        email_body = extract_text_from_html(email_body)

    email_kwargs = {
        'subject': subject, 'body': email_body, 'from_email': sender,
        'to': recipients
    }

    if headers is not None:
        email_kwargs['headers'] = headers

    message = EmailMessage(**email_kwargs)

    if not text_only:
        message.content_subtype = 'html'

    message.send()

    return message


def nested_dict(items, value=None):
    """Creates a nested, single-item dict from a list of items."""

    length = len(items)

    if length == 0:
        return {}
    elif length == 1:
        return {items[0]: value}
    else:
        return {items[0]: nested_dict(items[1:], value)}


def merge_dicts(first, second):
    """Merge two potentially nested dicts."""
    if not isinstance(second, dict):
        return second

    result = deepcopy(first)
    for key, value in second.iteritems():
        if key in result and isinstance(result[key], dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = deepcopy(value)

    return result


def query_to_json(data, sep="__"):
    """
    Expands a django query dictionary into one suitable for json encoding.
    """

    items = [(key.split(sep), value) for key, value in data.items()]
    dicts = [nested_dict(item[0], item[1]) for item in items]
    results = reduce(merge_dicts, dicts)

    return results


def json_to_query(data, sep="__", parent=""):
    """Collapse a dict into one suitable for django queries."""

    results = {}

    for key, value in data.items():
        if isinstance(value, dict):
            results.update(
                json_to_query(value, sep=sep, parent=parent + key + sep))
        else:
            results[parent + key] = value

    return results


def dict_identity(cls):
    """Give instances of a class more value like semantics.

    For this to work the instance members must also have value
    semantics.

    @dict_identity
    class Num(object):
        def __init__(self, val):
            self.val = val

    Num(2) == Num(3)
    >>> False
    Num(2) == Num(2) # Would have been False
    >>> True

    This is helpful for unit tests where a class represents some kind
    of value. It provides meaningful stringification and equality
    based on the members of the instance.
    """
    def eq(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        else:
            return False

    def ne(self, other):
        return not self.__eq__(other)

    def repr(self):
        return "<%s %r>" % (cls.__name__, self.__dict__)

    cls.__eq__ = eq
    cls.__ne__ = ne
    cls.__unicode__ = repr
    cls.__str__ = repr
    cls.__repr__ = repr
    return cls

@simplegeneric
def invitation_context(instance):
    """
    Returns a context dictionary to be used when rendering an invitation email.
    Minimally complete implementations should return a dictionary with a
    `message` key, which should be a string.

    Calling this function without arguments will raise a runtime error.

    """
    raise TypeError(
        "object of type '%s' has no invitation_context." % type(
            instance).__name__)

@invitation_context.register(str)
def str_invitation_reaason(string):
    """Returns the string verbatim as the `message`."""

    return {"message": (" " if string else "") + string + "."}


def autofocus_input(form, field_name=None):
    """
    Sets the autofocus attribute on one form field.

    Inputs:
    :form: The form we're examining
    :field_name: The field we're modifying. If none, we're modifying the first.
    """
    if field_name:
        # We can grab this field directly.
        field = form.fields[field_name]
    else:
        # We need to grab the first visible field.
        visible_fields = form.visible_fields()
        # visible_fields() returns a list of BoundFields. BoundField has a
        # field attribute which we can use to set autofocus.
        field = visible_fields[0].field
    field.widget.attrs.update({'autofocus': 'autofocus'})


def extract_value(obj, *attrs, **kwargs):
    """
    Traverse a value following named attributes.

    Inputs:
        :obj: The object to traverse for attributes.
        :attrs: Each positional argument is assumed to be the name of an
        attribute to access on the attribute which preceded it, or the object
        passed in if no attribute preceded it.
        :kwargs: The only recognized keyword argument is ``default``, which is
        the value returned if, after traversal, no matching attribute is found.
        If not specified, default is assumed to be ``None``.

    Output:
        Returns the value of the final attribute requested or default when such
        an attribute doesn't exist.

    Examples:
        >>> class Foo(object):
        ...    x = 7
        ...    y = 3


        >>> class Bar(object):
        ...    foo = Foo()
        ...    x = 9
        ...    y = 4

        >>> foo = Foo()
        >>> bar = Bar()
        >>> print extract_value(foo, 'x')
        7
        extract_value(foo, 'z')
        None
        extract_value(bar, 'foo', 'y')
        3
        extract_value(bar, 'y', 'q', default=8)
        8

    """
    default = kwargs.get('default', None)
    return reduce(lambda acc, x: getattr(acc, x, default), attrs, obj)


def make_chunks(l, n=1025):
    """
    Yield successive n-sized chunks from a list.

    """
    if connection.vendor == 'sqlite':
        # SQLite has a default maximum number of SQL variables of 999
        n = min(n, 999)
    for i in xrange(0, len(l), n):
        yield l[i:i+n]