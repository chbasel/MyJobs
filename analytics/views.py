from django.shortcuts import render_to_response
from django.template import RequestContext

def analytics_main(request):
    """
    View for analytics react module
    GET /analytics/view/main
    """
    ctx = {}

    return render_to_response('analytics/analytics_main.html', ctx,
                              RequestContext(request))
