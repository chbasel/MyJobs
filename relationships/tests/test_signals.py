from relationships.models import (DenormalizedSiteRelationship, Relationship,
                                  SiteRelationship)
from relationships.tests.base import RelationshipsBaseTest
from seo.models import SeoSite


class SignalsTest(RelationshipsBaseTest):
    def setUp(self):
        super(SignalsTest, self).setUp()
        self.by = Relationship.objects.create(type='test')

        domains = ['a.jobs', 'b.jobs', 'c.jobs', 'd.jobs', 'e.jobs', 'f.jobs']
        self.sites = [SeoSite.objects.create(domain=d) for d in domains]

    def test_post_save_update_relationships(self):
        """
        When a SiteRelationship is for two sites, a corresponding
        DenormalizedSiteRelationship should be created.

        """
        parent = self.sites[0]
        child = self.sites[1]

        SiteRelationship.objects.create(
            parent=parent, child=child, by=self.by
        )

        self.assertEqual(DenormalizedSiteRelationship.objects.count(), 1)

        denormalized = DenormalizedSiteRelationship.objects.first()
        self.assertEqual(denormalized.parent, parent)
        self.assertEqual(denormalized.child, child)
        self.assertEqual(denormalized.depth, 1)
        self.assertEqual(denormalized.by, self.by)

    def test_post_save_update_relationships_multiple(self):
        """
        When a SiteRelationship is added for two sites, corresponding
        DenormalizedSiteRelationships should be created for every site
        linked up to the parent up to depth N.

        """
        site_relationships = [
            # (parent, child, depth)
            (self.sites[0], self.sites[1], 1),
            (self.sites[1], self.sites[2], 2),
            (self.sites[2], self.sites[3], 3),
            (self.sites[0], self.sites[3], 1),
            (self.sites[4], self.sites[5], 1),
        ]

        for parent, child, depth in site_relationships:
            SiteRelationship.objects.create(
                parent=parent, child=child, by=self.by
            )

        # The following DenormalizedSiteRelationships should've been created:
        expected = [
            (self.sites[0], self.sites[1], 1),
            (self.sites[0], self.sites[2], 2),
            (self.sites[0], self.sites[3], 3),
            (self.sites[0], self.sites[3], 1),
            (self.sites[1], self.sites[2], 1),
            (self.sites[1], self.sites[3], 2),
            (self.sites[2], self.sites[3], 1),
            (self.sites[4], self.sites[5], 1)
        ]
        self.assertEqual(DenormalizedSiteRelationship.objects.count(),
                         len(expected))

        for parent, child, depth in expected:
            denormalized = DenormalizedSiteRelationship.objects.filter(
                parent=parent, child=child, depth=depth, by=self.by
            )
            self.assertTrue(denormalized.exists())

    def test_pre_delete_update_relationships(self):
        """
        When a SiteRelationship is deleted, all corresponding
        DenormalizedSiteRelationships should also be deleted.

        """
        parent = self.sites[0]
        child = self.sites[1]

        relationship = SiteRelationship.objects.create(
            parent=parent, child=child, by=self.by
        )

        self.assertEqual(DenormalizedSiteRelationship.objects.count(), 1)

        relationship.delete()

        self.assertEqual(DenormalizedSiteRelationship.objects.count(), 0)

    def test_pre_delete_update_relationships_multiple(self):
        """
        When a SiteRelationship deleted, all corresponding
        DenormalizedSiteRelationships should also be deleted. Un-related
        DenormalizedSiteRelationships should not be touched.

        """
        site_relationships = [
            # (parent, child, depth)
            (self.sites[0], self.sites[1], 1),
            (self.sites[1], self.sites[2], 2),
            (self.sites[2], self.sites[3], 3),
            (self.sites[0], self.sites[3], 1),
            (self.sites[4], self.sites[5], 1),
        ]

        for parent, child, depth in site_relationships:
            SiteRelationship.objects.create(
                parent=parent, child=child, by=self.by
            )

        # The following DenormalizedSiteRelationships should've been created:
        expected = [
            (self.sites[0], self.sites[1], 1),
            (self.sites[0], self.sites[2], 2),
            (self.sites[0], self.sites[3], 3),
            (self.sites[0], self.sites[3], 1),
            (self.sites[1], self.sites[2], 1),
            (self.sites[1], self.sites[3], 2),
            (self.sites[2], self.sites[3], 1),
            (self.sites[4], self.sites[5], 1)
        ]
        self.assertEqual(DenormalizedSiteRelationship.objects.count(),
                         len(expected))

        to_delete = site_relationships[0]
        SiteRelationship.objects.get(
            parent=to_delete[0], child=to_delete[1]
        ).delete()

        # The following should be the DenormalizedSiteRelationships after
        # the delete is completed:
        expected = [
            (self.sites[0], self.sites[3], 1),
            (self.sites[1], self.sites[2], 1),
            (self.sites[1], self.sites[3], 2),
            (self.sites[2], self.sites[3], 1),
            (self.sites[4], self.sites[5], 1)
        ]
        self.assertEqual(DenormalizedSiteRelationship.objects.count(),
                         len(expected))
        for parent, child, depth in expected:
            denormalized = DenormalizedSiteRelationship.objects.filter(
                parent=parent, child=child, depth=depth, by=self.by
            )
            self.assertTrue(denormalized.exists())
