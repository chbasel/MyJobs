from datetime import datetime

from unittest import TestCase

from myreports.datasources.partners import (
     PartnersDataSource, PartnersFilter)

from myjobs.tests.setup import MyJobsBase
from myjobs.tests.factories import UserFactory
from mydashboard.tests.factories import CompanyFactory
from mypartners.tests.factories import (
    PartnerFactory, ContactFactory, LocationFactory, TagFactory,
    ContactRecordFactory)
from mypartners.models import Status


class TestPartnersDataSource(MyJobsBase):
    def setUp(self):
        super(TestPartnersDataSource, self).setUp()

        # A company to work with
        self.company = CompanyFactory(name='right')
        self.company.save()

        # A separate company that should not show up in results.
        self.other_company = CompanyFactory(name='wrong')
        self.other_company.save()

        self.partner_a = PartnerFactory(
            owner=self.company,
            last_action_time='2015-09-30 13:23',
            uri='http://www.example.com/',
            data_source="zap",
            name="aaa")
        self.partner_b = PartnerFactory(
            owner=self.company,
            last_action_time='2015-10-03',
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

        self.east_tag = TagFactory.create(name='east', hex_color="aaaaaa")
        self.west_tag = TagFactory.create(name='west', hex_color="bbbbbb")
        self.bad_tag = TagFactory.create(name='bad', hex_color="cccccc")

        self.partner_a.tags.add(self.east_tag)
        self.partner_b.tags.add(self.west_tag)

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

        self.partner_a.primary_contact = self.john
        self.partner_b.primary_contact = self.sue

        self.partner_a.save()
        self.partner_b.save()

        # Archive archived data here. Doing this earlier in the set up results
        # in odd exceptions.
        self.partner_archived.archive()

    def test_run_unfiltered(self):
        """Make sure we only get data for this user."""
        ds = PartnersDataSource()
        recs = ds.run_unaggregated(self.company, PartnersFilter(), [])
        names = {r['name'] for r in recs}
        expected = {self.partner_a.name, self.partner_b.name}
        self.assertEqual(expected, names)
        expected_tags = {
            self.partner_a.pk: {'east'},
            self.partner_b.pk: {'west'},
        }

        def tags_by_pk(rec):
            return (rec['partner_id'], set(t['name'] for t in rec['tags']))

        found_tags = dict(tags_by_pk(r) for r in recs)

        self.assertEqual(expected_tags, found_tags)

    def test_run_count_comm_rec_per_month(self):
        """Make sure we only get data for this user."""
        for (subject, itx) in enumerate(['a', 'b', 'c']):
            for month in [2, 3, 4]:
                self.sue.contactrecord_set.add(
                    ContactRecordFactory(
                        subject=subject,
                        date_time=datetime(2015, month, 1)))

        ds = PartnersDataSource()
        recs = ds.run_count_comm_rec_per_month(
            self.company, PartnersFilter(), ['name', 'year', '-month'])
        data = [
            (r['name'], r['year'], r['month'], r['comm_rec_count'])
            for r in recs
        ]
        expected = [
            (self.partner_a.name, 2015, 12, 0),
            (self.partner_a.name, 2015, 11, 0),
            (self.partner_a.name, 2015, 10, 0),
            (self.partner_a.name, 2015, 9, 0),
            (self.partner_a.name, 2015, 8, 0),
            (self.partner_a.name, 2015, 7, 0),
            (self.partner_a.name, 2015, 6, 0),
            (self.partner_a.name, 2015, 5, 0),
            (self.partner_a.name, 2015, 4, 0),
            (self.partner_a.name, 2015, 3, 0),
            (self.partner_a.name, 2015, 2, 0),
            (self.partner_a.name, 2015, 1, 0),
            (self.partner_b.name, 2015, 12, 0),
            (self.partner_b.name, 2015, 11, 0),
            (self.partner_b.name, 2015, 10, 0),
            (self.partner_b.name, 2015, 9, 0),
            (self.partner_b.name, 2015, 8, 0),
            (self.partner_b.name, 2015, 7, 0),
            (self.partner_b.name, 2015, 6, 0),
            (self.partner_b.name, 2015, 5, 0),
            (self.partner_b.name, 2015, 4, 3),
            (self.partner_b.name, 2015, 3, 3),
            (self.partner_b.name, 2015, 2, 3),
            (self.partner_b.name, 2015, 1, 0),
        ]
        self.assertEqual(expected, data)

    def test_run_count_comm_rec_per_month_one_partner(self):
        """Trip over a bug in the mysql client driver."""
        for (subject, itx) in enumerate(['a', 'b', 'c']):
            for year in [2013, 2015, 2014]:
                for month in [2, 3, 4]:
                    self.sue.contactrecord_set.add(
                        ContactRecordFactory(
                            subject=subject,
                            date_time=datetime(year, month, 1)))

        ds = PartnersDataSource()
        partners_filter = PartnersFilter(tags=[['west']])
        recs = ds.run_count_comm_rec_per_month(
            self.company, partners_filter, ['name', 'year', '-month'])
        data = [
            (r['name'], r['year'], r['month'], r['comm_rec_count'])
            for r in recs
        ]
        self.assertEqual(36, len(data))

    def test_run_count_comm_rec_per_month_no_partners(self):
        """Trip over a bug in the mysql client driver."""
        for (subject, itx) in enumerate(['a', 'b', 'c']):
            for month in [2, 3, 4]:
                self.sue.contactrecord_set.add(
                    ContactRecordFactory(
                        subject=subject,
                        date_time=datetime(2015, month, 1)))

        ds = PartnersDataSource()
        partners_filter = PartnersFilter(tags=[['zzz']])
        recs = ds.run_count_comm_rec_per_month(
            self.company, partners_filter, ['name', 'year', '-month'])
        self.assertEqual(0, len(recs))

    def test_run_count_comm_rec_per_month_empty_partner(self):
        """One partner, no communication records."""
        ds = PartnersDataSource()
        partners_filter = PartnersFilter(tags=[['east']])
        recs = ds.run_count_comm_rec_per_month(
            self.company, partners_filter, ['name', 'year', '-month'])
        data = [
            (r['name'], r['year'], r['month'], r['comm_rec_count'])
            for r in recs
        ]
        self.assertEqual(12, len(data))
        default_year = datetime.now().year
        for item in data:
            self.assertEqual(default_year, item[1])
            self.assertEqual(0, item[3])

    def test_filter_by_date_range(self):
        """Should show only partner with last_action_time in range."""
        ds = PartnersDataSource()
        recs = ds.run_unaggregated(
            self.company,
            PartnersFilter(
                date=[datetime(2015, 9, 1), datetime(2015, 9, 30)]),
            [])
        names = {r['name'] for r in recs}
        expected = {self.partner_a.name}
        self.assertEqual(expected, names)

    def test_filter_by_date_before(self):
        """Should show only partner with last_action_time before date."""
        ds = PartnersDataSource()
        recs = ds.run_unaggregated(
            self.company,
            PartnersFilter(
                date=[None, datetime(2015, 9, 30)]),
            [])
        names = {r['name'] for r in recs}
        expected = {self.partner_a.name}
        self.assertEqual(expected, names)

    def test_filter_by_date_after(self):
        """Should show only partner with last_action_time after date."""
        ds = PartnersDataSource()
        recs = ds.run_unaggregated(
            self.company,
            PartnersFilter(
                date=[datetime(2015, 10, 1), None]),
            [])
        names = {r['name'] for r in recs}
        expected = {self.partner_b.name}
        self.assertEqual(expected, names)

    def test_filter_by_state(self):
        """Should show only partners with correct state."""
        ds = PartnersDataSource()
        recs = ds.run_unaggregated(
            self.company,
            PartnersFilter(
                locations={
                    'state': 'CA'
                }),
            [])
        names = [r['name'] for r in recs]
        expected = [self.partner_b.name]
        self.assertEqual(expected, names)

    def test_filter_by_city(self):
        """Should show only partners with correct city."""
        ds = PartnersDataSource()
        recs = ds.run_unaggregated(
            self.company,
            PartnersFilter(
                locations={
                    'city': 'Los Angeles'
                }),
            [])
        names = [r['name'] for r in recs]
        expected = [self.partner_b.name]
        self.assertEqual(expected, names)

    def test_filter_by_tags(self):
        """Show only partner with correct tags."""
        ds = PartnersDataSource()
        recs = ds.run_unaggregated(
            self.company,
            PartnersFilter(tags=[['EaSt']]),
            [])
        names = {r['name'] for r in recs}
        expected = {self.partner_a.name}
        self.assertEqual(expected, names)

    def test_filter_by_tags_or(self):
        """Show only partner with correct tags in 'or' configuration."""
        ds = PartnersDataSource()
        recs = ds.run_unaggregated(
            self.company,
            PartnersFilter(tags=[['EaSt', 'wEsT']]),
            [])
        names = {r['name'] for r in recs}
        expected = {self.partner_a.name, self.partner_b.name}
        self.assertEqual(expected, names)

    def test_filter_by_tags_and(self):
        """Show only partner with correct tags in 'and' configuration."""
        ds = PartnersDataSource()
        recs = ds.run_unaggregated(
            self.company,
            PartnersFilter(tags=[['EaSt'], ['wEsT']]),
            [])
        names = {r['name'] for r in recs}
        expected = set()
        self.assertEqual(expected, names)

        # Now try adding another tag.
        self.partner_a.tags.add(self.west_tag)
        recs = ds.run_unaggregated(
            self.company,
            PartnersFilter(tags=[['EaSt'], ['wEsT']]),
            [])
        names = {r['name'] for r in recs}
        expected = {self.partner_a.name}
        self.assertEqual(expected, names)

    def test_filter_by_data_source(self):
        """Check datasource filter works at all."""
        ds = PartnersDataSource()
        recs = ds.run_unaggregated(
            self.company,
            PartnersFilter(data_source="zap"),
            [])
        names = {r['name'] for r in recs}
        expected = {self.partner_a.name}
        self.assertEqual(expected, names)

    def test_filter_by_uri(self):
        """Check uri filter works at all."""
        ds = PartnersDataSource()
        recs = ds.run_unaggregated(
            self.company,
            PartnersFilter(uri="http://www.asdf.com/"),
            [])
        names = {r['name'] for r in recs}
        expected = {self.partner_b.name}
        self.assertEqual(expected, names)

    def test_filter_by_empty_things(self):
        """Empty filters should not filter, just like missing filters."""
        ds = PartnersDataSource()
        recs = ds.run_unaggregated(
            self.company,
            PartnersFilter(
                locations={'city': '', 'state': ''}),
            [])
        names = {r['name'] for r in recs}
        expected = {self.partner_a.name, self.partner_b.name}
        self.assertEqual(expected, names)

    def test_help_city(self):
        """Check city help works and ignores current city filter."""
        ds = PartnersDataSource()
        recs = ds.help_city(
            self.company,
            PartnersFilter(locations={'city': "zz"}),
            "angel")
        actual = {r['value'] for r in recs}
        self.assertEqual({'Los Angeles'}, actual)

    def test_help_state(self):
        """Check state help works and ignores current state filter."""
        ds = PartnersDataSource()
        recs = ds.help_state(
            self.company,
            PartnersFilter(locations={'state': "zz"}),
            "i")
        actual = {r['value'] for r in recs}
        self.assertEqual({'IL', 'IN'}, actual)

    def test_help_tags(self):
        """Check tags help works at all."""
        ds = PartnersDataSource()
        recs = ds.help_tags(self.company, PartnersFilter(), "E")
        actual = {r['value'] for r in recs}
        self.assertEqual({'east', 'west'}, actual)

    def test_help_tags_colors(self):
        """Tags should have colors"""
        ds = PartnersDataSource()
        recs = ds.help_tags(self.company, PartnersFilter(), "east")
        self.assertEqual("aaaaaa", recs[0]['hexColor'])

    def test_help_uri(self):
        """Check uri help works at all."""
        ds = PartnersDataSource()
        recs = ds.help_uri(
            self.company,
            PartnersFilter(),
            "ex")
        actual = {r['value'] for r in recs}
        self.assertEqual({'http://www.example.com/'}, actual)

    def test_help_data_source(self):
        """Check data_source help works at all."""
        ds = PartnersDataSource()
        recs = ds.help_data_source(
            self.company,
            PartnersFilter(),
            "z")
        actual = {r['value'] for r in recs}
        self.assertEqual({'zap'}, actual)

    def test_order(self):
        """Check ordering results works at all."""
        ds = PartnersDataSource()
        recs = ds.run_unaggregated(
            self.company,
            PartnersFilter(),
            ["-name"])
        names = [r['name'] for r in recs]
        expected = [self.partner_b.name, self.partner_a.name]
        self.assertEqual(expected, names)


class TestPartnersFilterCloning(TestCase):
    def test_clone_without_empty(self):
        """Cloning empty filters shouldn't crash."""
        filter = PartnersFilter()
        self.assertEqual(PartnersFilter(), filter.clone_without_city())
        self.assertEqual(PartnersFilter(), filter.clone_without_state())

    def test_clone_without_full(self):
        """Cloning should remove certain fields."""
        filter = PartnersFilter(
                tags=['C'],
                locations={'city': 'A', 'state': 'B'})
        expected_with_city = PartnersFilter(
                tags=['C'],
                locations={'city': 'A'})
        expected_with_state = PartnersFilter(
                tags=['C'],
                locations={'state': 'B'})
        expected_with_city_state_only = PartnersFilter(
                locations={'city': 'A', 'state': 'B'})
        self.assertEqual(expected_with_state, filter.clone_without_city())
        self.assertEqual(expected_with_city, filter.clone_without_state())
        self.assertEqual(
            expected_with_city_state_only,
            filter.clone_without_tags())
