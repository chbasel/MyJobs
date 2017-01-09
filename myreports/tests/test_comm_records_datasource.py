from datetime import datetime

from unittest import TestCase

from myreports.datasources.comm_records import (
    CommRecordsDataSource, CommRecordsFilter)
from myreports.datasources.util import (
    DateRangeFilter, CompositeAndFilter, MatchFilter,
    OrGroupFilter, AndGroupFilter, UnlinkedFilter)

from myjobs.tests.setup import MyJobsBase
from myjobs.tests.factories import UserFactory
from seo.tests.factories import CompanyFactory
from mypartners.tests.factories import (
    PartnerFactory, ContactFactory, LocationFactory, TagFactory,
    ContactRecordFactory)
from mypartners.models import Status


class TestCommRecordsDataSource(MyJobsBase):
    def setUp(self):
        super(TestCommRecordsDataSource, self).setUp()

        # A company to work with
        self.company = CompanyFactory(name='right')
        self.company.save()

        # A separate company that should not show up in results.
        self.other_company = CompanyFactory(name='wrong')
        self.other_company.save()

        self.partner_a = PartnerFactory(
            owner=self.company,
            uri='http://www.example.com/',
            data_source="zap",
            name="aaa")
        self.partner_b = PartnerFactory(
            owner=self.company,
            uri='http://www.asdf.com/',
            data_source="bcd",
            name="bbb")
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
        self.north_tag = TagFactory.create(
            company=self.company, name='north', hex_color="cccccc")
        self.south_tag = TagFactory.create(
            company=self.company, name='south', hex_color="dddddd")
        self.left_tag = TagFactory.create(
            company=self.company, name='left', hex_color="eeeeee")
        self.right_tag = TagFactory.create(
            company=self.company, name='right', hex_color="ffffff")
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
        self.john.tags.add(self.north_tag)

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
        self.sue.tags.add(self.south_tag)

        self.partner_a.primary_contact = self.john
        self.partner_b.primary_contact = self.sue

        self.partner_a.save()
        self.partner_b.save()

        self.record_1 = ContactRecordFactory(
            subject='record 1',
            date_time='2015-09-30 13:23',
            contact=self.john,
            contact_type="Email",
            partner=self.partner_a,
            location='Indianapolis, IN',
            tags=[self.east_tag])
        self.record_2 = ContactRecordFactory(
            subject='record 2',
            date_time='2015-01-01',
            contact=self.john,
            contact_type="Meeting Or Event",
            partner=self.partner_a,
            location='Indianapolis, IN',
            tags=[self.east_tag])
        self.record_3 = ContactRecordFactory(
            subject='record 3',
            date_time='2015-10-03',
            contact=self.sue,
            contact_type="Phone",
            partner=self.partner_b,
            location='Los Angeles, CA',
            tags=[self.west_tag])

        # Archive archived data here. Doing this earlier in the set up results
        # in odd exceptions.
        self.partner_archived.archive()

    def test_run_unfiltered(self):
        """Make sure we only get data for this user."""
        ds = CommRecordsDataSource()
        recs = ds.run_unaggregated(self.company, CommRecordsFilter(), [])
        subjects = {r['subject'] for r in recs}
        expected = {
            self.record_1.subject,
            self.record_2.subject,
            self.record_3.subject,
        }
        self.assertEqual(expected, subjects)

    def test_filter_by_date_range(self):
        """Should show only commrec with last_action_time in range."""
        ds = CommRecordsDataSource()
        date_range = DateRangeFilter([
            datetime(2015, 9, 1),
            datetime(2015, 9, 30)])
        recs = ds.run_unaggregated(
            self.company,
            CommRecordsFilter(date_time=date_range),
            [])
        subjects = {r['subject'] for r in recs}
        expected = {self.record_1.subject}
        self.assertEqual(expected, subjects)

    def test_filter_by_date_before(self):
        """Should show only commrec with last_action_time before date."""
        ds = CommRecordsDataSource()
        date_range = DateRangeFilter(
            [None, datetime(2015, 9, 30)])
        recs = ds.run_unaggregated(
            self.company,
            CommRecordsFilter(date_time=date_range),
            [])
        subjects = {r['subject'] for r in recs}
        expected = {self.record_1.subject, self.record_2.subject}
        self.assertEqual(expected, subjects)

    def test_filter_by_date_after(self):
        """Should show only commrec with last_action_time after date."""
        ds = CommRecordsDataSource()
        date_range = DateRangeFilter(
            [datetime(2015, 10, 1), None])
        recs = ds.run_unaggregated(
            self.company,
            CommRecordsFilter(date_time=date_range),
            [])
        subjects = {r['subject'] for r in recs}
        expected = {self.record_3.subject}
        self.assertEqual(expected, subjects)

    def test_filter_by_state(self):
        """Should show only commrecs with correct state."""
        ds = CommRecordsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            CommRecordsFilter(
                locations=CompositeAndFilter({'state': MatchFilter('CA')})),
            [])
        subjects = {r['subject'] for r in recs}
        expected = {self.record_3.subject}
        self.assertEqual(expected, subjects)

    def test_filter_by_city(self):
        """Should show only commrecs with correct city."""
        ds = CommRecordsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            CommRecordsFilter(
                locations=CompositeAndFilter({
                    'city': MatchFilter('Los Angeles')})),
            [])
        subjects = {r['subject'] for r in recs}
        expected = {self.record_3.subject}
        self.assertEqual(expected, subjects)

    def test_filter_by_tags(self):
        """
        Show only commrec with correct tags.

        """
        ds = CommRecordsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            CommRecordsFilter(tags=AndGroupFilter([
                OrGroupFilter([MatchFilter('EaSt')])])),
            [])
        subjects = {r['subject'] for r in recs}
        expected = {self.record_1.subject, self.record_2.subject}
        self.assertEqual(expected, subjects)

    def test_filter_by_tags_unlinked(self):
        """
       Only return untagged commrecs.

        """
        self.record_1.tags.clear()
        ds = CommRecordsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            CommRecordsFilter(tags=UnlinkedFilter()),
            [])
        subjects = {r['subject'] for r in recs}
        expected = {self.record_1.subject}
        self.assertEqual(expected, subjects)

    def test_filter_by_tags_or(self):
        """Show only commrec with correct tags in 'or' configuration."""
        ds = CommRecordsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            CommRecordsFilter(tags=AndGroupFilter([
                OrGroupFilter([MatchFilter('EaSt'), MatchFilter('wEsT')])])),
            [])
        subjects = {r['subject'] for r in recs}
        expected = {
            self.record_1.subject,
            self.record_2.subject,
            self.record_3.subject,
        }
        self.assertEqual(expected, subjects)

    def test_filter_by_tags_and(self):
        """Show only commrec with correct tags in 'and' configuration."""
        ds = CommRecordsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            CommRecordsFilter(tags=AndGroupFilter([
                OrGroupFilter([MatchFilter('EaSt')]),
                OrGroupFilter([MatchFilter('wEsT')])])),
            [])
        subjects = {r['subject'] for r in recs}
        expected = set()
        self.assertEqual(expected, subjects)

        # Now try adding another tag.
        self.record_1.tags.add(self.west_tag)
        self.record_1.save()
        recs = ds.run_unaggregated(
            self.company,
            CommRecordsFilter(tags=AndGroupFilter([
                OrGroupFilter([MatchFilter('EaSt')]),
                OrGroupFilter([MatchFilter('wEsT')])])),
            [])
        subjects = {r['subject'] for r in recs}
        expected = {self.record_1.subject}
        self.assertEqual(expected, subjects)

    def test_filter_by_communication_type(self):
        """Check communication_type filter works at all."""
        ds = CommRecordsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            CommRecordsFilter(communication_type=OrGroupFilter([
                MatchFilter('email')])),
            [])
        subjects = {r['subject'] for r in recs}
        expected = {self.record_1.subject}
        self.assertEqual(expected, subjects)

    def test_filter_by_partner(self):
        """
        Check partner filter works at all.

        """
        ds = CommRecordsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            CommRecordsFilter(
                partner=OrGroupFilter([MatchFilter(self.partner_a.pk)])),
            [])
        subjects = {r['subject'] for r in recs}
        expected = {self.record_1.subject, self.record_2.subject}
        self.assertEqual(expected, subjects)

    def test_filter_by_contact(self):
        """
        Check partner filter works at all.

        """
        ds = CommRecordsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            CommRecordsFilter(
                contact=OrGroupFilter([MatchFilter(self.sue.pk)])),
            [])
        subjects = {r['subject'] for r in recs}
        expected = {self.record_3.subject}
        self.assertEqual(expected, subjects)

    def test_filter_by_contact_tags(self):
        """
        Test that we can filter by contact tags.

        """
        ds = CommRecordsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            CommRecordsFilter(
                contact_tags=AndGroupFilter([
                    OrGroupFilter([MatchFilter('sOuTh')])])),
            [])
        subjects = {r['subject'] for r in recs}
        expected = {self.record_3.subject}
        self.assertEqual(expected, subjects)

    def test_filter_by_contact_tags_untagged(self):
        """
        Check that we can find a record attached to an untagged contact.

        """
        self.sue.tags.clear()
        ds = CommRecordsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            CommRecordsFilter(contact_tags=UnlinkedFilter()),
            [])
        subjects = {r['subject'] for r in recs}
        expected = {self.record_3.subject}
        self.assertEqual(expected, subjects)

    def test_filter_by_partner_tags(self):
        """
        Test that we can filter by partner tags.

        """
        ds = CommRecordsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            CommRecordsFilter(
                partner_tags=AndGroupFilter([
                    OrGroupFilter([MatchFilter('rigHt')])])),
            [])
        subjects = {r['subject'] for r in recs}
        expected = {self.record_3.subject}
        self.assertEqual(expected, subjects)

    def test_filter_by_partner_tags_untagged(self):
        """
        Check that we can find a record attached to an untagged partner.

        """
        self.partner_b.tags.clear()
        ds = CommRecordsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            CommRecordsFilter(partner_tags=UnlinkedFilter()),
            [])
        subjects = {r['subject'] for r in recs}
        expected = {self.record_3.subject}
        self.assertEqual(expected, subjects)

    def test_help_city(self):
        """
        Check city help works and ignores current city filter.

        """
        ds = CommRecordsDataSource()
        recs = ds.help_city(
            self.company,
            CommRecordsFilter(
                locations=CompositeAndFilter({
                    'city': MatchFilter("zz")})),
            "angel")
        actual = {r['value'] for r in recs}
        self.assertEqual({'Los Angeles'}, actual)

    def test_help_state(self):
        """
        Check state help works and ignores current state filter.

        """
        ds = CommRecordsDataSource()
        recs = ds.help_state(
            self.company,
            CommRecordsFilter(
                locations=CompositeAndFilter({
                    'state': MatchFilter("zz")})),
            "i")
        actual = {r['value'] for r in recs}
        self.assertEqual({'IL', 'IN'}, actual)

    def test_help_tags(self):
        """
        Check tags help works at all.

        """
        ds = CommRecordsDataSource()
        recs = ds.help_tags(self.company, CommRecordsFilter(), "E")
        actual = {r['value'] for r in recs}
        self.assertEqual({'east', 'west'}, actual)

    def test_help_contact_tags(self):
        """
        Check contact tags help works at all.

        """
        ds = CommRecordsDataSource()
        recs = ds.help_contact_tags(self.company, CommRecordsFilter(), "O")
        actual = {r['value'] for r in recs}
        self.assertEqual({'north', 'south'}, actual)

    def test_help_partner_tags(self):
        """
        Check partner tags help works at all.

        """
        ds = CommRecordsDataSource()
        recs = ds.help_partner_tags(self.company, CommRecordsFilter(), "t")
        actual = {r['value'] for r in recs}
        self.assertEqual({'left', 'right'}, actual)

    def test_help_tags_colors(self):
        """
        Tags should have colors

        """
        ds = CommRecordsDataSource()
        recs = ds.help_tags(self.company, CommRecordsFilter(), "east")
        self.assertEqual("aaaaaa", recs[0]['hexColor'])

    def test_help_communication_types(self):
        """
        Check communication_types help works at all.

        """
        ds = CommRecordsDataSource()
        recs = ds.help_communication_type(
            self.company, CommRecordsFilter(), "ph")
        actual = {r['value'] for r in recs}
        expected = {'phone', 'job', 'meetingorevent', 'email', 'pssemail'}
        self.assertEqual(expected, actual)

    def test_help_partner(self):
        """
        Check partner help works at all.

        """
        ds = CommRecordsDataSource()
        recs = ds.help_partner(self.company, CommRecordsFilter(), "A")
        self.assertEqual(
            [{'value': self.partner_a.pk, 'display': self.partner_a.name}],
            recs)

    def test_help_contact(self):
        """
        Check contact help works at all.

        """
        ds = CommRecordsDataSource()
        recs = ds.help_contact(self.company, CommRecordsFilter(), "U")
        self.assertEqual(
            [{'value': self.sue.pk, 'display': self.sue.name}],
            recs)

    def test_values(self):
        """
        Check limiting values works at all

        """
        self.maxDiff = 10000
        ds = CommRecordsDataSource()
        recs = ds.run_unaggregated(
            self.company,
            CommRecordsFilter(),
            ["partner", "subject"])
        expected = [
            {'partner': u'aaa', 'subject': u'record 1'},
            {'partner': u'aaa', 'subject': u'record 2'},
            {'partner': u'bbb', 'subject': u'record 3'},
        ]
        self.assertEqual(expected, recs)

    def test_adorn_filter(self):
        self.maxDiff = 10000
        found_filter_items = {
            'tags': ['east', 'west'],
            'communication_type': ['Email'],
            'partner': [str(self.partner_a.pk)],
            'contact': [str(self.sue.pk)],
            'contact_tags': ['nOrth', 'south'],
            'partner_tags': ['lEft', 'riGht'],
        }

        expected = {
            u'partner': {
                self.partner_a.pk:
                    {'value': self.partner_a.pk, 'display': u'aaa'},
            },
            u'contact': {
                self.sue.pk:
                    {'value': self.sue.pk, 'display': u'Sue Baxter'},
            },
            u'tags': {
                u'east': {
                    'value': u'east',
                    'display': u'east',
                    'hexColor': u'aaaaaa',
                },
                u'west': {
                    'value': u'west',
                    'display': u'west',
                    'hexColor': u'bbbbbb',
                },
            },
            u'communication_type': {
                'email': {'value': 'email', 'display': 'Email'}
            },
            u'contact_tags': {
                u'north': {
                    'value': u'north',
                    'display': u'north',
                    'hexColor': u'cccccc',
                },
                u'south': {
                    'value': u'south',
                    'display': u'south',
                    'hexColor': u'dddddd',
                },
            },
            u'partner_tags': {
                u'left': {
                    'value': u'left',
                    'display': u'left',
                    'hexColor': u'eeeeee',
                },
                u'right': {
                    'value': u'right',
                    'display': u'right',
                    'hexColor': u'ffffff',
                },
            },
        }

        ds = CommRecordsDataSource()
        result = ds.adorn_filter_items(self.company, found_filter_items)
        self.assertEqual(expected, result)

    def test_default_filter(self):
        """
        should produce a populated filter object.

        """
        ds = CommRecordsDataSource()
        default_filter = ds.get_default_filter(None, self.company)
        self.assertEquals(
            datetime.now().year,
            default_filter.date_time.dates[1].year)
        # Take out value dated today. Too hard to run through assertEquals.
        default_filter.date_time.dates[1] = None
        expected = CommRecordsFilter(
            date_time=DateRangeFilter([datetime(2014, 1, 1), None]))
        self.assertEquals(expected, default_filter)


class TestCommRecordsFilterCloning(TestCase):
    def test_clone_without_empty(self):
        """
        Cloning empty filters shouldn't crash.

        """
        filter = CommRecordsFilter()
        self.assertEqual(CommRecordsFilter(), filter.clone_without_city())
        self.assertEqual(CommRecordsFilter(), filter.clone_without_state())

    def test_clone_without_full(self):
        """
        Cloning should remove certain fields.

        """
        filter = CommRecordsFilter(
                tags=['C'],
                locations=CompositeAndFilter({
                    'city': MatchFilter('A'),
                    'state': MatchFilter('B')}))
        expected_with_city = CommRecordsFilter(
                tags=['C'],
                locations=CompositeAndFilter({
                    'city': MatchFilter('A')}))
        expected_with_state = CommRecordsFilter(
                tags=['C'],
                locations=CompositeAndFilter({
                    'state': MatchFilter('B')}))
        self.assertEqual(expected_with_state, filter.clone_without_city())
        self.assertEqual(expected_with_city, filter.clone_without_state())

    def test_clone_without_contacts(self):
        filter = CommRecordsFilter(
                contact=[1, 2, 3],
                locations={'city': 'A', 'state': 'B'})
        expected_filter = CommRecordsFilter(
                locations={'city': 'A', 'state': 'B'})
        self.assertEqual(
            expected_filter,
            filter.clone_without_contact())

    def test_clone_without_partners(self):
        filter = CommRecordsFilter(
                partner=[1, 2, 3],
                locations={'city': 'A', 'state': 'B'})
        expected_filter = CommRecordsFilter(
                locations={'city': 'A', 'state': 'B'})
        self.assertEqual(
            expected_filter,
            filter.clone_without_partner())
