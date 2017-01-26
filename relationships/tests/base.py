from django.test import TestCase

from relationships.models import Relationship
from seo.models import SeoSite


class RelationshipsBaseTest(TestCase):
    def setUp(self):
        super(RelationshipsBaseTest, self).setUp()
        self.by = Relationship.objects.create(type='test')

        domains = ['a.jobs', 'b.jobs', 'c.jobs', 'd.jobs', 'e.jobs', 'f.jobs']
        self.sites = [SeoSite.objects.create(domain=d) for d in domains]