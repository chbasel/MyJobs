from datetime import datetime

from unittest import TestCase

from myreports.datasources.contacts import (
    ContactsDataSource, ContactsFilter)

from myreports.datasources.util import (
    DateRangeFilter, CompositeAndFilter, MatchFilter,
    OrGroupFilter, AndGroupFilter, UnlinkedFilter)

from myjobs.tests.setup import MyJobsBase
from myjobs.tests.factories import UserFactory
from seo.tests.factories import CompanyFactory
from mypartners.tests.factories import (
    PartnerFactory, ContactFactory, LocationFactory, TagFactory)
from mypartners.models import Status


class TestContactsDataSource(MyJobsBase):
    def setUp(self):
        super(TestContactsDataSource, self).setUp()

        # A company to work with
        self.company = CompanyFactory(name='right')
        self.company.save()

        # A separate company that should not show up in results.
        self.other_company = CompanyFactory(name='wrong')
        self.other_company.save()

        self.partner = PartnerFactory(
            owner=self.company)
        self.other_partner = PartnerFactory(
            owner=self.other_company)

        self.partner_a = PartnerFactory(owner=self.company, name="aaa")
        self.partner_b = PartnerFactory(owner=self.company, name="bbb")
        # An unapproved parther. Associated data should be filtered out.
        self.partner_unapp = PartnerFactory(
            owner=self.company,
            name="unapproved",
            approval_status__code=Status.UNPROCESSED)
        # An archived parther. Associated data should be filtered out.
        self.partner_archived = PartnerFactory(owner=self.company)

        self.east_tag = TagFactory.create(
            company=self.company, name='east', hex_color="aaaaaa")
        self.west_tag = TagFactory.create(
            company=self.company, name='west', hex_color="bbbbbb")
        self.left_tag = TagFactory.create(
            company=self.company, name='left', hex_color="cccccc")
        self.right_tag = TagFactory.create(
            company=self.company, name='right', hex_color="dddddd")
        self.bad_tag = TagFactory.create(
            company=self.company, name='bad', hex_color="cccccc")

        self.partner_a.tags.add(self.left_tag)
        self.partner_b.tags.add(self.right_tag)

        self.john_user = UserFactory(email="john@user.com")
        self.john = ContactFactory(
            partner=self.partner_a,
            name='john adams',
            user=self.john_user,
            email="john@user.com",
            last_action_time='2015-10-03')
        self.john.locations.add(
            LocationFactory.create(
                city="Indianapolis",
                state="IN"))
        self.john.locations.add(
            LocationFactory.create(
                city="Chicago",
                state="IL"))
        self.john.tags.add(self.east_tag)

        self.sue_user = UserFactory(email="sue@user.com")
        self.sue = ContactFactory(
            partner=self.partner_b,
            name='Sue Baxter',
            user=self.sue_user,
            email="sue@user.com",
            last_action_time='2015-09-30 13:23')
        self.sue.locations.add(
            LocationFactory.create(
                address_line_one="123",
                city="Los Angeles",
                state="CA"))
        self.sue.locations.add(
            LocationFactory.create(
                address_line_one="234",
                city="Los Angeles",
                state="CA"))
        self.sue.tags.add(self.west_tag)

        # Poision data. Should never show up.
        self.archived_partner_user = (
            UserFactory(email="archived_partner@user.com"))
        self.archived_partner = ContactFactory(
            partner=self.partner_archived,
            name='Archived Partner Contact',
            user=self.archived_partner_user,
            email="archived_partner@user.com",
            last_action_time='2015-09-30 13:23')
        self.archived_partner.locations.add(
            LocationFactory.create(
                address_line_one="123",
                city="Nowhere",
                state="NO"))
        self.archived_partner.locations.add(
            LocationFactory.create(
                address_line_one="234",
                city="Nowhere",
                state="NO"))
        self.archived_partner.tags.add(self.west_tag)

        # Poision data. Should never show up.
        self.archived_contact_user = (
            UserFactory(email="archived_contact@user.com"))
        self.archived_contact = ContactFactory(
            partner=self.partner_b,
            name='Archived Contact',
            user=self.archived_contact_user,
            email="archived_contact@user.com",
            last_action_time='2015-09-30 13:23')
        self.archived_contact.locations.add(
            LocationFactory.create(
                address_line_one="123",
                city="Nowhere",
                state="NO"))
        self.archived_contact.locations.add(
            LocationFactory.create(
                address_line_one="234",
                city="Nowhere",
                state="NO"))
        self.archived_contact.tags.add(self.west_tag)

        # Poision data. Should never show up.
        self.unapproved_partner_user = (
            UserFactory(email="unapproved_partner@user.com"))
        self.unapproved_partner_contact = ContactFactory(
            partner=self.partner_unapp,
            name='Unapproved Partner Contact',
            user=self.unapproved_partner_user,
            email="unapproved_partner@user.com",
            last_action_time='2015-09-30 13:23')
        self.unapproved_partner_contact.locations.add(
            LocationFactory.create(
                address_line_one="123",
                city="Nowhere",
                state="NO"))
        self.unapproved_partner_contact.locations.add(
            LocationFactory.create(
                address_line_one="234",
                city="Nowhere",
                state="NO"))
        self.unapproved_partner_contact.tags.add(self.west_tag)

        # Poision data. Should never show up.
        self.unapproved_contact_user = (
            UserFactory(email="unapproved_contact@user.com"))
        self.unapproved_contact = ContactFactory(
            partner=self.partner_b,
            name='Unapproved Contact',
            user=self.unapproved_contact_user,
            email="unapproved_contact@user.com",
            last_action_time='2015-09-30 13:23',
            approval_status__code=Status.UNPROCESSED)
        self.unapproved_contact.locations.add(
            LocationFactory.create(
                address_line_one="123",
                city="Nowhere",
                state="NO"))
        self.unapproved_contact.locations.add(
            LocationFactory.create(
                address_line_one="234",
                city="Nowhere",
                state="NO"))
        self.unapproved_contact.tags.add(self.west_tag)

        # Poision data. Should never show up.
        self.wrong_user = UserFactory(email="wrong@user.com")
        self.wrong = ContactFactory(
            partner=self.other_partner,
            name='wrong person',
            user=self.wrong_user,
            email="wrong@user.com",
            last_action_time='2015-09-03')
        self.wrong.locations.add(
            LocationFactory.create(
                city="Los Angeles",
                state="CA"))
        self.wrong.tags.add(self.east_tag)
        self.wrong.tags.add(self.west_tag)
        self.wrong.tags.add(self.bad_tag)

        # Archive archived data here. Doing this earlier in the set up results
        # in odd exceptions.
        self.partner_archived.archive()
        self.archived_contact.archive()

    def test_run_unfiltered(self):
        """
        Make sure we only get data for this user.

        """
        ds = ContactsDataSource()
        recs = ds.run_unaggregated(self.company, ContactsFilter(), [])
        names = {r['name'] for r in recs}
        expected = {self.sue.name, self.john.name}
        self.assertEqual(expected, names)

    def test_filter_by_date_range(self):
        """
        Should show only contact with last_action_time in range.

        """
        ds = ContactsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            ContactsFilter(
                date=DateRangeFilter([
                    datetime(2015, 9, 1),
                    datetime(2015, 9, 30)])),
            [])
        names = {r['name'] for r in recs}
        expected = {self.sue.name}
        self.assertEqual(expected, names)

    def test_filter_by_date_before(self):
        """
        Should show only contact with last_action_time before date.

        """
        ds = ContactsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            ContactsFilter(
                date=DateRangeFilter([None, datetime(2015, 9, 30)])),
            [])
        names = {r['name'] for r in recs}
        expected = {self.sue.name}
        self.assertEqual(expected, names)

    def test_filter_by_date_after(self):
        """
        Should show only contact with last_action_time after date.

        """
        ds = ContactsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            ContactsFilter(
                date=DateRangeFilter([datetime(2015, 10, 1), None])),
            [])
        names = {r['name'] for r in recs}
        expected = {self.john.name}
        self.assertEqual(expected, names)

    def test_filter_by_tags(self):
        """
        Should show only contact with correct tags.

        """
        ds = ContactsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            ContactsFilter(tags=AndGroupFilter([
                OrGroupFilter([MatchFilter('EaSt')])])),
            [])
        names = {r['name'] for r in recs}
        expected = {self.john.name}
        self.assertEqual(expected, names)

    def test_filter_by_tags_or(self):
        """
        Show only contact with correct tags in 'or' configuration.

        """
        ds = ContactsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            ContactsFilter(tags=AndGroupFilter([
                OrGroupFilter([MatchFilter('EaSt'), MatchFilter('wEsT')])])),
            [])
        names = {r['name'] for r in recs}
        expected = {self.john.name, self.sue.name}
        self.assertEqual(expected, names)

    def test_filter_by_tags_and(self):
        """
        Show only contact with correct tags in 'and' configuration.

        """
        ds = ContactsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            ContactsFilter(tags=AndGroupFilter([
                OrGroupFilter([MatchFilter('EaSt')]),
                OrGroupFilter([MatchFilter('wEsT')])])),
            [])
        names = {r['name'] for r in recs}
        expected = set()
        self.assertEqual(expected, names)

        # Now try adding another tag.
        self.john.tags.add(self.west_tag)
        recs = ds.run_unaggregated(
            self.company,
            ContactsFilter(tags=AndGroupFilter([
                OrGroupFilter([MatchFilter('EaSt')]),
                OrGroupFilter([MatchFilter('wEsT')])])),
            [])
        names = {r['name'] for r in recs}
        expected = {self.john.name}
        self.assertEqual(expected, names)

    def test_filter_untagged(self):
        """
        This indicates that the member selected to filter by untagged.

        """
        self.sue.tags.clear()
        ds = ContactsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            ContactsFilter(tags=UnlinkedFilter()),
            [])
        names = {r['name'] for r in recs}
        expected = {self.sue.name}
        self.assertEqual(expected, names)

    def test_filter_by_state(self):
        """Should show only contacts with correct state."""
        ds = ContactsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            ContactsFilter(
                locations=CompositeAndFilter({'state': MatchFilter('CA')})),
            [])
        names = [r['name'] for r in recs]
        expected = [self.sue.name]
        self.assertEqual(expected, names)

    def test_filter_by_city(self):
        """Should show only contacts with correct city."""
        ds = ContactsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            ContactsFilter(
                locations=CompositeAndFilter({
                    'city': MatchFilter('Los Angeles')})),
            [])
        names = [r['name'] for r in recs]
        expected = [self.sue.name]
        self.assertEqual(expected, names)

    def test_filter_by_partners(self):
        """Should filter by partners."""
        ds = ContactsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            ContactsFilter(
                partner=OrGroupFilter([MatchFilter(self.partner_a.pk)])),
            [])
        subjects = {r['name'] for r in recs}
        expected = {self.john.name}
        self.assertEqual(expected, subjects)

    def test_filter_by_partner_tags(self):
        """
        Test that we can filter by partner tags.

        """
        ds = ContactsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            ContactsFilter(partner_tags=AndGroupFilter([
                OrGroupFilter([MatchFilter('rigHt')])])),
            [])
        subjects = {r['name'] for r in recs}
        expected = {self.sue.name}
        self.assertEqual(expected, subjects)

    def test_filter_by_partner_tags_untagged(self):
        """
        Check that we can find a record attached to an untagged partner.

        """
        self.partner_b.tags.clear()
        ds = ContactsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            ContactsFilter(partner_tags=UnlinkedFilter()),
            [])
        subjects = {r['name'] for r in recs}
        expected = {self.sue.name}
        self.assertEqual(expected, subjects)

    def test_help_city(self):
        """Check city help works and ignores current city filter."""
        ds = ContactsDataSource()
        recs = ds.help_city(
            self.company,
            ContactsFilter(
                locations=CompositeAndFilter({
                    'city': MatchFilter('Los Angeles')})),
            "angel")
        actual = {r['value'] for r in recs}
        self.assertEqual({'Los Angeles'}, actual)

    def test_help_state(self):
        """Check state help works and ignores current state filter."""
        ds = ContactsDataSource()
        recs = ds.help_state(
            self.company,
            ContactsFilter(
                locations=CompositeAndFilter({
                    'state': MatchFilter('zz')})),
            "i")
        actual = {r['value'] for r in recs}
        self.assertEqual({'IL', 'IN'}, actual)

    def test_help_tags(self):
        """Check tags help works at all."""
        ds = ContactsDataSource()
        recs = ds.help_tags(self.company, ContactsFilter(), "E")
        actual = {r['value'] for r in recs}
        self.assertEqual({'east', 'west'}, actual)

    def test_help_partner_tags(self):
        """
        Check partner tags help works at all.

        """
        ds = ContactsDataSource()
        recs = ds.help_partner_tags(self.company, ContactsFilter(), "t")
        actual = {r['value'] for r in recs}
        self.assertEqual({'left', 'right'}, actual)

    def test_help_tags_colors(self):
        """Tags should have colors"""
        ds = ContactsDataSource()
        recs = ds.help_tags(self.company, ContactsFilter(), "east")
        self.assertEqual("aaaaaa", recs[0]['hexColor'])

    def test_help_partner(self):
        """Check partner help works at all."""
        ds = ContactsDataSource()
        recs = ds.help_partner(self.company, ContactsFilter(), "A")
        self.assertEqual(
            [{'value': self.partner_a.pk, 'display': 'aaa'}],
            recs)

    def test_values(self):
        """Check limiting values works at all."""
        ds = ContactsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            ContactsFilter(),
            ["name", "email"])
        expected = [
            {'name': self.john.name, 'email': u'john@user.com'},
            {'name': self.sue.name, 'email': u'sue@user.com'},
        ]
        self.assertEqual(expected, recs)

    def test_adorn_filter(self):
        self.maxDiff = 10000
        found_filter_items = {
            'tags': ['east', 'west'],
            'partner': [str(self.partner_a.pk)],
            'partner_tags': ['lEft', 'Right'],
        }
        expected = {
            u'partner': {
                self.partner_a.pk:
                    {'value': self.partner_a.pk, 'display': u'aaa'},
            },
            u'tags': {
                'east': {
                    'value': u'east',
                    'display': u'east',
                    'hexColor': u'aaaaaa',
                },
                'west': {
                    'value': u'west',
                    'display': u'west',
                    'hexColor': u'bbbbbb',
                },
            },
            u'partner_tags': {
                'left': {
                    'value': u'left',
                    'display': u'left',
                    'hexColor': u'cccccc',
                },
                'right': {
                    'value': u'right',
                    'display': u'right',
                    'hexColor': u'dddddd',
                },
            },
        }

        ds = ContactsDataSource()
        adorned_filter = ds.adorn_filter_items(
            self.company, found_filter_items)
        self.assertEqual(expected, adorned_filter)

    def test_default_filter(self):
        """should produce a populated filter object."""
        ds = ContactsDataSource()
        default_filter = ds.get_default_filter(None, self.company)
        self.assertEquals(
            datetime.now().year,
            default_filter.date.dates[1].year)
        # Take out value dated today. Too hard to run through assertEquals.
        default_filter.date.dates[1] = None
        expected = ContactsFilter(
            date=DateRangeFilter([datetime(2014, 1, 1), None]))
        self.assertEquals(expected, default_filter)


class TestContactsFilterCloning(TestCase):
    def test_clone_without_empty(self):
        """Cloning empty filters shouldn't crash."""
        filter = ContactsFilter()
        self.assertEqual(ContactsFilter(), filter.clone_without_city())
        self.assertEqual(ContactsFilter(), filter.clone_without_state())

    def test_clone_without_full(self):
        """Cloning should remove certain fields."""
        filter = ContactsFilter(
                tags=['C'],
                locations=CompositeAndFilter({
                    'city': MatchFilter('A'),
                    'state': MatchFilter('B')}))
        expected_with_city = ContactsFilter(
                tags=['C'],
                locations=CompositeAndFilter({
                    'city': MatchFilter('A')}))
        expected_with_state = ContactsFilter(
                tags=['C'],
                locations=CompositeAndFilter({
                    'state': MatchFilter('B')}))
        self.assertEqual(expected_with_state, filter.clone_without_city())
        self.assertEqual(expected_with_city, filter.clone_without_state())

    def test_clone_without_partners(self):
        locations_filter = CompositeAndFilter({
            'city': MatchFilter('A'), 'state': MatchFilter('B')})
        filter = ContactsFilter(partner=[1, 2, 3], locations=locations_filter)
        expected_without_partners = ContactsFilter(locations=locations_filter)
        self.assertEqual(
            expected_without_partners,
            filter.clone_without_partner())
