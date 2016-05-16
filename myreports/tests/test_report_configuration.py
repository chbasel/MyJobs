from datetime import datetime

from unittest import TestCase

from myreports.report_configuration import (
    ReportConfiguration, ColumnConfiguration)


class TestReportConfig(TestCase):
    def setUp(self):
        super(TestReportConfig, self).setUp()
        # Realistic contacts report configuration
        self.contacts_config = ReportConfiguration(
            columns=[
                ColumnConfiguration(
                    column='name',
                    format='text'),
                ColumnConfiguration(
                    column='partner',
                    format='text',
                    filter_interface='search_multiselect',
                    filter_display='Partners'),
                ColumnConfiguration(
                    column='email',
                    format='text'),
                ColumnConfiguration(
                    column='phone',
                    format='text'),
                ColumnConfiguration(
                    column='date',
                    format='us_date',
                    filter_interface='date_range',
                    filter_display='Date'),
                ColumnConfiguration(
                    column='notes',
                    format='text'),
                ColumnConfiguration(
                    column='locations',
                    format='city_state_list',
                    filter_interface='city_state',
                    filter_display='Locations'),
                ColumnConfiguration(
                    column='tags',
                    format='comma_sep',
                    filter_interface='search_multiselect',
                    filter_display='Tags'),
            ])

        # Realistic extracted contact records.
        self.test_data = [
            {
                'date': datetime(2015, 10, 3),
                'email': u'john@user.com',
                'locations': [
                    {'city': u'Indianapolis', 'state': u'IN'},
                    {'city': u'Chicago', 'state': u'IL'}
                ],
                'name': u'john adams',
                'notes': u'',
                'partner': u'aaa',
                'phone': u'84104391',
                'tags': [u'east']
            },
            {
                'date': datetime(2015, 9, 30),
                'email': u'sue@user.com',
                'locations': [
                    {'city': u'Los Angeles', 'state': u'CA'},
                ],
                'name': u'Sue Baxter',
                'notes': u'',
                'partner': u'bbb',
                'phone': u'84104391',
                'tags': [u'west']
            }
        ]

    def test_header(self):
        """Test that the formatter can get an ordered list of columns."""
        header = self.contacts_config.get_header()
        self.assertEqual([
            'name', 'partner', 'email', 'phone', 'date', 'notes',
            'locations', 'tags'],
            header)

    def test_records(self):
        """Test that records are formatted properly."""
        self.maxDiff = 10000
        rec = self.contacts_config.format_record(self.test_data[0], [])
        self.assertEqual({
            'name': 'john adams',
            'partner': 'aaa',
            'email': 'john@user.com',
            'phone': '84104391',
            'date': '10/03/2015',
            'notes': '',
            'locations': "Indianapolis, IN, Chicago, IL",
            'tags': 'east',
            }, rec)
        rec = self.contacts_config.format_record(self.test_data[1], [])
        self.assertEqual({
            'name': 'Sue Baxter',
            'partner': 'bbb',
            'email': 'sue@user.com',
            'phone': '84104391',
            'date': '09/30/2015',
            'notes': '',
            'locations': 'Los Angeles, CA',
            'tags': 'west',
            }, rec)

    def test_formatting_limit_columns(self):
        """Test that records contain only desired columns."""
        self.maxDiff = 10000
        rec = self.contacts_config.format_record(
            self.test_data[0],
            ['partner', 'name'])
        self.assertEqual({
            'name': 'john adams',
            'partner': 'aaa',
            }, rec)

    def test_formatting_ignores_invalid_columns(self):
        """Test that records contain only desired and valid columns."""
        self.maxDiff = 10000
        rec = self.contacts_config.format_record(
            self.test_data[0],
            ['partner', 'name', 'ZZZZZ'])
        self.assertEqual({
            'name': 'john adams',
            'partner': 'aaa',
            }, rec)


class TestColumnConfiguration(TestCase):
    def test_trivial(self):
        """Test that we can format a simple value."""
        test_data = {'name': 'asdf'}
        self.assertEqual(
            'asdf',
            ColumnConfiguration(
                column='name',
                format='text').extract_formatted(test_data))

    def test_deep_join(self):
        """Test that we can format a complex value."""
        test_data = {
            'locations': [
                {'city': 'Indy', 'state': 'IN'},
                {'city': 'Chicago', 'state': 'IL'},
            ],
        }
        self.assertEqual(
            'Indy, IN, Chicago, IL',
            ColumnConfiguration(
                column='locations',
                format='city_state_list').extract_formatted(test_data))
