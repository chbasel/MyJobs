from urlparse import urlparse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.core.urlresolvers import reverse

from myjobs.decorators import requires


@requires("view analytics")
def analytics_main(request):
    """
    View for analytics react module
    GET /analytics/view/main
    """

    absolute = urlparse(settings.ABSOLUTE_URL)
    pathed = absolute._replace(path=reverse(analytics_main))
    ctx = {
        'base_href': pathed.geturl(),
    }

    return render_to_response('analytics/analytics_main.html', ctx,
                              RequestContext(request))
