from django.conf import settings
from django.contrib.admin import site
from django.core.urlresolvers import reverse
from django.apps import apps

from myjobs.models import User
from myjobs.tests.setup import MyJobsBase
from seo.tests.setup import DirectSEOBase


def admin_test(self):
    """
    Tests add and list views for all models registered with the Django
    admin.
    """
    self.password = 'imbatmancalifornia'
    self.user = User.objects.create_superuser(password=self.password,
                                              email='bc@batyacht.com')
    self.user.save()
    self.client.login(email=self.user.email,
                      password=self.password)
    # The list of registered admin pages starts out blank until we force
    # the url cache to fill.
    self.client.get('/')

    admins = []
    for app in settings.PROJECT_APPS:
        for model_name in apps.get_app_config(app).models:
            try:
                # site._registry is a dictionary of Model:ModelAdmin mappings.
                model = apps.get_model(app, model_name)
                admins.append(site._registry[model])
            except KeyError:
                # Not all models are in the admin (myjobs.Ticket, for example).
                pass
    # admin.urls on the inner for loop contains all urls, including edit
    # and history. We only care about add and list.
    urls = []
    for admin in admins:
        for url in admin.urls:
            if hasattr(url, 'name') and url.name != None and url.name.endswith(('_add', '_changelist')):
                urls.append(reverse('admin:' + url.name))

    # Ensure we have something to test.
    self.assertTrue(len(urls) > 0)
    for url in urls:
        response = self.client.get(url)
        # Not all entries (currently postajob/purchasedproduct) have add pages.
        # Those that don't have add pages return 403 status codes.
        self.assertIn(response.status_code, [200, 403])


class SEOAdminTests(DirectSEOBase):
    test_admin_add_and_list = admin_test


class MyJobsAdminTests(MyJobsBase):
    test_admin_add_and_list = admin_test
