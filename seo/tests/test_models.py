# -*- coding: utf-8 -*-
from mock import patch

from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.template.loader import TemplateDoesNotExist
from django.test import TestCase

from seo.tests import factories
from seo.models import Company, CustomFacet, SeoSite, SiteTag, SiteRelationship
from myjobs.tests.factories import AppAccessFactory
from myjobs.tests.factories import RoleFactory
from seo.tests.setup import DirectSEOBase


from seo.models import (build_graph, get_all_children, sort_children_by_weight,
                        weight_children_by_terms)


class SeoSiteRelatedSitesTest(TestCase):
    def setUp(self):
        """
        Creates a site family of sites, with a circular relationship.


        parent.jobs == term ==> term.jobs  == term ==> expression.jobs == term ==> word.jobs           ==region==> somewhere.jobs
                                           ==region==> placeterm.jobs  ==region==> smallplaceterm.jobs ==region==> smallplace.jobs
                    ==region==> place.jobs == term ==> placeterm.jobs
                                           ==region==> smallplace.jobs

        """
        super(SeoSiteRelatedSitesTest, self).setUp()
        SeoSite.objects.all().delete()
        self.parent = SeoSite.objects.create(domain='parent.jobs')

        family = {
            'parent.jobs': {
                'term': ['term.jobs'],
                'region': ['place.jobs']
            },
            'term.jobs': {
                'term': ['expression.jobs'],
                'region': ['placeterm.jobs']
            },
            'place.jobs': {
                'term': ['placeterm.jobs'],
                'region': ['smallplace.jobs']
            },
            'placeterm.jobs': {
                'term': [],
                'region': ['smallplaceterm.jobs']
            },
            'smallplace.jobs': {
                'term': [],
                'region': []
            },
            'smallplaceterm.jobs': {
                'term': [],
                'region': ['smallplace.jobs']
            },
            'word.jobs': {
                'term': [],
                'region': ['somewhere.jobs']
            },
            'somewhere.jobs': {
                'term': [],
                'region': []
            },
            'expression.jobs': {
                'term': [],
                'region': []
            }
          }

        self.children_depth_1 = set(family[self.parent.domain]['term'] +
                                    family[self.parent.domain]['region'])
        self.term_depth_1 = set(family[self.parent.domain]['term'])

        self.children_depth_2 = set()
        self.term_depth_2 = set()
        for child in self.children_depth_1:
            [self.children_depth_2.add(c) for c in family[child]['term'] +
             family[child]['region']]
        for child in self.term_depth_1:
            [self.term_depth_2.add(c) for c in family[child]['term']]

        self.children_depth_3 = set()
        for child in self.children_depth_2:
            [self.children_depth_3.add(c) for c in family[child]['term'] +
             family[child]['region']]
        self.term_depth_3 = set()
        for child in self.term_depth_2:
            [self.term_depth_3.add(c) for c in family[child]['term']]

        for site in family.keys():
            site, _ = SeoSite.objects.get_or_create(domain=site)

            for child in family[site.domain]['term']:
                child, _ = SeoSite.objects.get_or_create(domain=child)
                SiteRelationship.objects.create(parent=site, child=child,
                                                by='term')

            for child in family[site.domain]['region']:
                child, _ = SeoSite.objects.get_or_create(domain=child)
                SiteRelationship.objects.create(parent=site, child=child,
                                                by='region')

    def test_related_sites(self):
        related_sites = SeoSite.objects.related_sites(self.parent)
        related_sites = set(related_sites.values_list('domain', flat=True))
        expected = self.children_depth_1
        self.assertItemsEqual(related_sites, expected)

    def test_related_sites_depth_2(self):
        related_sites = SeoSite.objects.related_sites(self.parent, depth=2)
        related_sites = set(related_sites.values_list('domain', flat=True))
        expected = self.children_depth_1 | self.children_depth_2
        self.assertItemsEqual(related_sites, expected)

    def test_related_sites_depth_3(self):
        related_sites = SeoSite.objects.related_sites(self.parent, depth=3)
        related_sites = set(related_sites.values_list('domain', flat=True))
        expected = self.children_depth_1 | self.children_depth_2 | self.children_depth_3

        self.assertItemsEqual(related_sites, expected)

    def test_related_sites_by(self):
        related_sites = SeoSite.objects.related_sites(self.parent, by='term')
        related_sites = set(related_sites.values_list('domain', flat=True))
        expected = self.term_depth_1
        self.assertItemsEqual(related_sites, expected)

    def test_related_sites_depth_2_by(self):
        related_sites = SeoSite.objects.related_sites(self.parent, depth=2,
                                                      by='term')
        related_sites = set(related_sites.values_list('domain', flat=True))
        expected = self.term_depth_1 | self.term_depth_2
        self.assertItemsEqual(related_sites, expected)

    def test_related_sites_depth_3_by(self):
        related_sites = SeoSite.objects.related_sites(self.parent, depth=3,
                                                      by='term')
        related_sites = set(related_sites.values_list('domain', flat=True))
        expected = self.term_depth_1 | self.term_depth_2 | self.term_depth_3
        self.assertItemsEqual(related_sites, expected)

    def test_get_all_children(self):
        graph = build_graph()
        related_sites = get_all_children(graph, self.parent.domain)
        related_sites = [site[0] for site in related_sites]
        expected = self.children_depth_1
        self.assertItemsEqual(set(related_sites), expected)

    def test_get_all_children_depth_2(self):
        graph = build_graph()
        related_sites = get_all_children(graph, self.parent.domain, depth=2)
        related_sites = [site[0] for site in related_sites]
        expected = self.children_depth_1 | self.children_depth_2
        self.assertItemsEqual(set(related_sites), expected)

    def test_get_all_children_depth_3(self):
        graph = build_graph()
        related_sites = get_all_children(graph, self.parent.domain, depth=3)
        related_sites = [site[0] for site in related_sites]
        expected = (self.children_depth_1 | self.children_depth_2 |
                    self.children_depth_3)
        self.assertItemsEqual(set(related_sites), expected)

    def test_get_all_children_by(self):
        graph = build_graph()
        related_sites = get_all_children(graph, self.parent.domain, by='term')
        related_sites = [site[0] for site in related_sites]
        expected = self.term_depth_1
        self.assertItemsEqual(set(related_sites), expected)

    def test_get_all_children_depth_2_by(self):
        graph = build_graph()
        related_sites = get_all_children(graph, self.parent.domain, depth=2,
                                         by='term')
        related_sites = [site[0] for site in related_sites]
        expected = self.term_depth_1 | self.term_depth_2
        self.assertItemsEqual(set(related_sites), expected)

    def test_get_all_children_depth_3_by(self):
        graph = build_graph()
        related_sites = get_all_children(graph, self.parent.domain, depth=3,
                                         by='term')
        related_sites = [site[0] for site in related_sites]
        expected = self.term_depth_1 | self.term_depth_2 | self.term_depth_3
        self.assertItemsEqual(set(related_sites), expected)

    def test_sort_children_by_weight(self):
        children = [
            ('fourth.jobs', 97), ('first.jobs', 50), ('second.jobs', 6),
            ('sixth.jobs', 95),  ('fifth.jobs', 96), ('second.jobs', 90),
            ('third.jobs', 98), ('first.jobs', 50), ('second.jobs', 3)
        ]
        expected = [
            'first.jobs', 'second.jobs', 'third.jobs', 'fourth.jobs',
            'fifth.jobs', 'sixth.jobs'
        ]
        results = sort_children_by_weight(children)
        for result, actual in zip(results, expected):
            self.assertEqual(result[0], actual)

    def test_weight_children_by_term(self):
        children = [
            ('same.jobs', 10),
            ('differentbecauseterm.jobs', 10),
            ('differentbecauseword.jobs', 10)
        ]
        expected = [
            ('same.jobs', 10),
            ('differentbecauseterm.jobs', 20),
            ('differentbecauseword.jobs', 20)
        ]

        results = weight_children_by_terms(children, ['term', 'word'])
        self.assertItemsEqual(results, expected)


class ModelsTestCase(DirectSEOBase):
    """
    All tests that probe the *custom* functionality of models in the seo
    app belong here.

    """
    @patch('newrelic.agent.add_custom_parameter')
    @patch('django.template.loader.get_template')
    def test_configuration_get_template_is_v1(self, mock_get_template,
                                              mock_add_custom_param):
        """
        Configurations on v1 should not get the v2 template, even if a
        v2 template is available.

        django.template.loader.get_template is patched to ensure that
        the requested template does exist.

        """
        v1 = 'v1'
        template_string = 'this/does_not_exist'
        configuration = factories.ConfigurationFactory(template_version=v1)

        actual_template_string = configuration.get_template(template_string)

        self.assertEqual(template_string, actual_template_string)
        # New Relic should also be receiving the correct information.
        mock_add_custom_param.assert_called_with("template_version", v1)

    @patch('newrelic.agent.add_custom_parameter')
    @patch('django.template.loader.get_template')
    def test_configuration_get_template_fail(self, mock_get_template,
                                             mock_add_custom_param):
        """
        Configurations on v2 templates should still get the v1 template if
        no v2 template is available.

        django.template.loader.get_template is patched to ensure that
        the requested template does not exist.
        """
        mock_get_template.side_effect = TemplateDoesNotExist

        v2 = 'v2'
        template_string = 'this/does_not_exist'
        configuration = factories.ConfigurationFactory(template_version=v2)
        self.assertEqual(configuration.template_version, v2)

        actual_template_string = configuration.get_template(template_string)

        self.assertEqual(template_string, actual_template_string)
        # New Relic should also be receiving the correct information.
        mock_add_custom_param.assert_called_with("template_version", "v1")

    @patch('newrelic.agent.add_custom_parameter')
    @patch('django.template.loader.get_template')
    def test_configuration_get_template_is_v2(self, mock_get_template,
                                              mock_add_custom_param):
        """
        If a Configuration is on v2 and a v2 template is available, the v2
        template string should be the the one returned.

        django.template.loader.get_template is patched to ensure that
        the requested template does exist.

        """
        v2 = 'v2'
        template_string = 'this/does_not_exist'
        expected_template_string = "%s/%s" % (v2, template_string)
        configuration = factories.ConfigurationFactory(template_version=v2)

        actual_template_string = configuration.get_template(template_string)

        self.assertEqual(expected_template_string, actual_template_string)
        # New Relic should also be receiving the correct information.
        mock_add_custom_param.assert_called_with("template_version", v2)

    def test_unique_redirect(self):
        """
        Test to ensure that we can't create a redirect for the same
        SeoSite more than once (enforcing the "unique_together"
        constraint on the SeoSiteRedirect model.

        """
        site = factories.SeoSiteFactory()
        factories.SeoSiteRedirectFactory(seosite=site)
        ssr2 = factories.SeoSiteRedirectFactory.build()
        self.assertRaises(IntegrityError, ssr2.save, ())

    def test_config_inc(self):
        """
        Test that the Configuration instances associated with a
        particular SeoSite instance have their ``revision`` value
        incremented when the SeoSite is saved.

        """
        site = factories.SeoSiteFactory.build()
        site.save()
        config_staging = factories.ConfigurationFactory.build()
        config_staging.save()
        config_prod = factories.ConfigurationFactory.build(status=2)
        config_prod.save()
        site.configurations = [config_staging, config_prod]
        # The default value for the `revision` attribute is 1, and it's
        # incremented on save, so that means that even on the first save it gets
        # incremented to 2. So that's why we're testing against [2, 2] for two
        # new Configuration instances instead of [1, 1].
        self.assertItemsEqual([c.revision for c in site.configurations.all()],
                              [2, 2])
        # Make some arbitrary change to the SeoSite instance.
        site.site_heading = "We're changing the header! Call the cops!"
        site.save()
        self.assertItemsEqual([c.revision for c in site.configurations.all()],
                              [3, 3])

    def test_invalid_custom_facet(self):
        facet = CustomFacet()
        facet.city = facet.state = facet.country = facet.title = ' '
        facet.querystring = ")"
        self.assertRaises(ValidationError, facet.save)

    def test_child_nonchainfk_works_in_valid_relationships(self):
        """
            Verify that a NonChainedForeignKey field will allow a typical
            one to many relationship with children elements.

            Uses SeoSite.parent_site as example field.
        """
        failed = False
        parent_site = factories.SeoSiteFactory()
        child_sites = [factories.SeoSiteFactory() for x in range(0,9)]
        for child in child_sites:
            child.parent_site = parent_site
            child.clean_fields()
            child.save()

    def test_child_nonchainfk_cant_have_children(self):
        """
            Verify that a NonChainedForeignKey field that has a parent_site entry
            cannot be made the parent of another NonChainedForeignKey field.

            Uses SeoSite.parent_site as example field.
        """
        parent_site = factories.SeoSiteFactory()
        child_site = factories.SeoSiteFactory()
        grandchild_site = factories.SeoSiteFactory()
        child_site.parent_site = parent_site
        child_site.save()
        grandchild_site.parent_site = child_site
        with self.assertRaises(ValidationError):
            grandchild_site.clean_fields()
        with self.assertRaises(ValidationError):
            grandchild_site.save()

    def test_parent_nonchainfk_cannot_become_child(self):
        """
            Verify that a NonChainedForeignKey field that has child sites cannot
            become the child of another NonChainedForeignKey field.

            Uses SeoSite.parent_site as example field.
        """
        initial_parent_site = factories.SeoSiteFactory()
        child_site = factories.SeoSiteFactory()
        super_parent_site = factories.SeoSiteFactory()
        child_site.parent_site = initial_parent_site
        child_site.save()
        initial_parent_site.parent_site = super_parent_site
        with self.assertRaises(ValidationError):
            initial_parent_site.clean_fields()
        with self.assertRaises(ValidationError):
            initial_parent_site.save()

    def test_nonchainfk_cant_be_its_own_parent(self):
        """
            Verify that a NonChainedForeignKey field cannot be its own parent.

            Uses SeoSite.parent_site as example field.
        """
        orphan_site = factories.SeoSiteFactory()
        orphan_site.parent_site = orphan_site
        with self.assertRaises(ValidationError):
            orphan_site.clean_fields()
        with self.assertRaises(ValidationError):
            orphan_site.save()

    def test_new_company_gets_admin_role(self):
        """
        When a new company is created, that company should have an Admin Role
        available to it.
        """

        company = Company.objects.create(name="Test Company")
        self.assertIn('Admin', company.role_set.values_list('name', flat=True))


class TestRoles(DirectSEOBase):
    """
    These tests are meant to ensure that roles act as a sufficient replacement
    for company users.
    """

    def setUp(self):
        super(TestRoles, self).setUp()

        self.user = factories.UserFactory()
        self.business_unit = factories.BusinessUnitFactory()
        self.company = factories.CompanyFactory()
        self.company.job_source_ids.add(self.business_unit)
        self.site = factories.SeoSiteFactory()
        self.site.business_units.add(self.business_unit)

    def test_seosite_user_has_access(self):
        """
        Tests that a user has access if that user can be tied back to one of
        the companies associated with an seo site's business units.
        """

        # user not assigned a role in company, so shouldn't have access
        self.assertFalse(self.site.user_has_access(self.user))

        role = RoleFactory(company=self.company)
        self.user.roles.add(role)
        self.assertTrue(self.site.user_has_access(self.user))

    def test_company_user_has_access(self):
        """
        Test that a user has access if the user can be tied to a company.
        """

        # user not assigned a role in company, so shouldn't have access
        self.assertFalse(self.company.user_has_access(self.user))

        role = RoleFactory(company=self.company)
        self.user.roles.add(role)
        self.assertTrue(self.company.user_has_access(self.user))

    def test_admin_count(self):
        """
        SeoSite.admins.count() should return the number of users who can be
        tied back to that company as an admin.

        """


        # can't use create_batch since emails need to be unique and
        # updating the User model disrupts other tests
        users = [factories.UserFactory(email="alice%s@gmail.com" % i)
                 for i in range(10)]

        # When activities are enabled, company user count is determined by
        # the number distinct users assigned a role within that company
        role = RoleFactory(company=self.company, name='Admin')
        self.assertEqual(self.company.admins.count(), 0)

        for user in users:
            user.roles = [role]
        self.assertEqual(self.company.admins.count(), 10)


class SeoSitePostAJobFiltersTestCase(DirectSEOBase):
    def setUp(self):
        super(SeoSitePostAJobFiltersTestCase, self).setUp()
        self.company = factories.CompanyFactory()
        self.company_buid = factories.BusinessUnitFactory()
        self.company.job_source_ids.add(self.company_buid)

    def create_generic_sites(self):
        sites = []
        for x in range(1, 15):
            factories.SeoSiteFactory()
        return sites

    def create_multiple_sites_for_company(self):
        sites = []
        for x in range(1, 15):
            site = factories.SeoSiteFactory()
            site.business_units.add(self.company_buid)
            site.save()
            sites.append(site)
        return sites

    def create_multiple_network_sites(self):
        network_tag, _ = SiteTag.objects.get_or_create(site_tag='network')

        sites = []
        for x in range(1, 15):
            site = factories.SeoSiteFactory()
            site.site_tags.add(network_tag)
            site.save()
            sites.append(site)
        return sites

    def test_network_sites(self):
        network_sites = self.create_multiple_network_sites()
        self.create_multiple_sites_for_company()
        self.create_generic_sites()

        kwargs = {'postajob_filter_type': 'network sites only'}
        new_site = factories.SeoSiteFactory(**kwargs)

        postajob_sites = new_site.postajob_site_list()
        postajob_site_ids = [site.id for site in postajob_sites]

        self.assertEqual(len(postajob_sites), len(network_sites))
        [self.assertIn(site.pk, postajob_site_ids) for site in network_sites]
        self.assertNotIn(new_site.pk, postajob_site_ids)

    def test_network_sites_and_this_site(self):
        network_sites = self.create_multiple_network_sites()
        self.create_multiple_sites_for_company()
        self.create_generic_sites()

        kwargs = {'postajob_filter_type': 'network sites and this site'}
        new_site = factories.SeoSiteFactory(**kwargs)

        postajob_sites = new_site.postajob_site_list()
        postajob_site_ids = [site.id for site in postajob_sites]

        self.assertEqual(len(postajob_sites), len(network_sites)+1)
        [self.assertIn(site.pk, postajob_site_ids) for site in network_sites]
        self.assertIn(new_site.pk, postajob_site_ids)

    def test_this_site_only(self):
        network_sites = self.create_multiple_network_sites()
        self.create_multiple_sites_for_company()
        self.create_generic_sites()

        # 'this site only' is the default.
        new_site = factories.SeoSiteFactory()

        postajob_sites = new_site.postajob_site_list()
        postajob_site_ids = [site.id for site in postajob_sites]

        self.assertEqual(len(postajob_sites), 1)
        [self.assertNotIn(site.pk, postajob_site_ids) for site in network_sites]
        self.assertIn(new_site.pk, postajob_site_ids)

    def test_company_sites(self):
        self.create_multiple_network_sites()
        company_sites = self.create_multiple_sites_for_company()
        self.create_generic_sites()

        kwargs = {'postajob_filter_type': 'sites associated with the company '
                                          'that owns this site'}
        new_site = factories.SeoSiteFactory(**kwargs)
        new_site.business_units.add(self.company_buid)
        new_site.save()

        postajob_sites = new_site.postajob_site_list()
        postajob_site_ids = [site.id for site in postajob_sites]

        # postajob_sites = company_sites + new_site
        self.assertEqual(len(postajob_sites), len(company_sites)+1)
        [self.assertIn(site.pk, postajob_site_ids) for site in company_sites]

    def test_network_and_company_sites(self):
        network_sites = self.create_multiple_network_sites()
        company_sites = self.create_multiple_sites_for_company()
        self.create_generic_sites()

        kwargs = {'postajob_filter_type': 'network sites and sites associated '
                                          'with the company that owns this '
                                          'site'}
        new_site = factories.SeoSiteFactory(**kwargs)
        new_site.business_units.add(self.company_buid)
        new_site.save()

        postajob_sites = new_site.postajob_site_list()
        postajob_site_ids = [site.id for site in postajob_sites]

        # postajob_sites = company_sites + network_sites + new_site
        self.assertEqual(len(postajob_sites),
                         len(company_sites)+len(network_sites)+1)
        [self.assertIn(site.pk, postajob_site_ids) for site in company_sites]
        [self.assertIn(site.pk, postajob_site_ids) for site in network_sites]

    def test_all_sites(self):
        self.create_multiple_network_sites()
        self.create_multiple_sites_for_company()
        self.create_generic_sites()

        kwargs = {'postajob_filter_type': 'all sites'}
        new_site = factories.SeoSiteFactory(**kwargs)
        new_site.business_units.add(self.company_buid)
        new_site.save()

        postajob_sites = new_site.postajob_site_list()

        # postajob_sites = company_sites + network_sites + generic_sites +
        #                  new_site
        self.assertEqual(len(postajob_sites), SeoSite.objects.all().count())

    def test_enabled_access(self):
        """
        `Company.enabled_access` should return  list of app access names.
        """
        self.assertItemsEqual(self.company.enabled_access, [])

        app_access = AppAccessFactory(name='Test Access')
        self.company.app_access.add(app_access)

        self.assertItemsEqual(self.company.enabled_access, ['Test Access'])
