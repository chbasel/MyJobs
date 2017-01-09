import json

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, RedirectView

from redirect.models import ViewSource
from seo.forms import settings_forms


class EmailDomainFormView(View):
    base_template_context = {
        'custom_action': 'Edit',
        'display_name': 'Email Domains'
    }
    template = 'postajob/form.html'

    def success_url(self):
        return reverse('purchasedmicrosite_admin_overview')

    def get(self, request):
        form = settings_forms.EmailDomainForm(request=request)
        kwargs = dict(self.base_template_context)
        kwargs.update({
            'form': form,
        })
        return render_to_response(self.template, kwargs,
                                  context_instance=RequestContext(request))

    def post(self, request):
        form = settings_forms.EmailDomainForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.success_url())
        kwargs = dict(self.base_template_context)
        kwargs.update({
            'form': form,
        })
        return render_to_response(self.template, kwargs,
                                  context_instance=RequestContext(request))


def secure_redirect(request, page):
    """
    Redirects to the correct path on secure.my.jobs if this is not a network
    site, or 404 if it is.
    """
    if settings.SITE.site_tags.filter(site_tag='network').exists():
        return RedirectView.as_view(
            url='https://secure.my.jobs/%s' % page)(request)
    else:
        raise Http404("seo.views.settings_views.secure_redirect: not a "
                      "network site")


@csrf_exempt
def get_view_sources(request):
    """
    Authenticates the user then returns a list of view sources.
    """
    creds = json.loads(request.body)
    user = authenticate(username=creds.get('un', ''),
                        password=creds.get('pw', ''))
    if user and user.is_staff:
        vs_list = map(lambda vs: {'name': vs.name,
                                  'friendly_name': vs.friendly_name,
                                  'id': vs.view_source_id},
                      ViewSource.objects.all())
        return HttpResponse(json.dumps(vs_list))
    else:
        raise Http404("seo.views.settings_views.get_view_sources: not a "
                      "staff user")
