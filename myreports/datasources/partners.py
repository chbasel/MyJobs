"""Partners DataSource"""
from datetime import datetime

from mypartners.models import Contact, Partner, Status, Location, Tag

from postajob.location_data import states

from myreports.datasources.util import (
    dispatch_help_by_field_name, dispatch_run_by_data_type,
    extract_tags, apply_filter_to_queryset, adorn_filter,
    NoFilter, CompositeAndFilter, DateRangeFilter)
from myreports.datasources.base import DataSource, DataSourceFilter
from myreports.datasources.sql import (
    count_comm_rec_per_month_per_partner_sql)
from myreports.datasources.rowstream import (
    DjangoField, from_django, DjangoRowBuilder,
    from_cursor, sort_stream, from_list)

from universal.helpers import dict_identity

from django.db import connection


class PartnersDataSource(DataSource):
    partner_row_builder = DjangoRowBuilder([
        DjangoField('id', rename='partner_id'),
        DjangoField('data_source'),
        DjangoField('last_action_time', rename='date'),
        DjangoField('name'),
        DjangoField('primary_contact.name', rename='primary_contact'),
        DjangoField('tags', transform=extract_tags),
        DjangoField('uri')])

    def run(self, data_type, company, filter_spec, values):
        return dispatch_run_by_data_type(
            self, data_type, company, filter_spec, values)

    def filtered_partners(self, company, filter_spec):
        qs_filtered = filter_spec.filter_partners(company)
        qs_distinct = qs_filtered.distinct()
        return qs_distinct

    def run_unaggregated(self, company, filter_spec, values):
        qs_filtered = filter_spec.filter_partners(company)
        qs_optimized = qs_filtered.prefetch_related(
            'tags', 'primary_contact')

        partners = from_django(self.partner_row_builder, qs_optimized, values)
        return list(partners)

    def run_count_comm_rec_per_month(self, company, filter_spec, values):
        # Get a list of valid partners (according to our filter).
        qs_filtered = filter_spec.filter_partners(company)
        partner_ids = list(qs_filtered.values_list('id', flat=True))

        # If there are no partners, we're done.
        if not partner_ids:
            return []

        sql = count_comm_rec_per_month_per_partner_sql
        cursor = connection.cursor()
        cursor.execute(sql, {'partner_list': partner_ids})
        count_stream = from_cursor(cursor)

        # Iterate over counts results.
        # Find year range and organize counts for later.
        min_year = None
        max_year = None
        db_counts = {}
        for record in count_stream:
            partner_id = record['partner_id']
            year = record['year']
            month = record['month']
            comm_rec_count = record['comm_rec_count']

            if year < min_year or min_year is None:
                min_year = year
            if year > max_year or max_year is None:
                max_year = year

            key = (partner_id, year, month)
            db_counts[key] = comm_rec_count

        # If there are no communication records, assume current year.
        if not db_counts:
            min_year = datetime.now().year
            max_year = min_year

        # Create full range of time slots with counts.
        # DB won't fill in zero's without a complex query.
        # Do this instead.
        full_counts = {}
        for partner_id in partner_ids:
            count_list = []
            full_counts[partner_id] = count_list
            for year in xrange(min_year, max_year + 1):
                for month in xrange(1, 12 + 1):
                    key = (partner_id, year, month)
                    if key in db_counts:
                        count = db_counts[key]
                        count_list.append((year, month, count))
                    else:
                        count_list.append((year, month, 0))

        qs_optimized = qs_filtered.prefetch_related('tags', 'primary_contact')
        partners = from_django(self.partner_row_builder, qs_optimized)

        # Join the two streams
        joined_fields = partners.fields + ['year', 'month', 'comm_rec_count']
        joined_data = []
        for partner_record in partners:
            count_list = full_counts.get(partner_record['partner_id'], [])
            for count_tuple in count_list:
                year, month, count = count_tuple
                joined_record = dict(partner_record)
                joined_record.update({
                    'year': year,
                    'month': month,
                    'comm_rec_count': count,
                    })
                joined_data.append(joined_record)
        joined = from_list(joined_fields, joined_data)

        return list(joined)

    def filter_type(self):
        return PartnersFilter

    def help(self, company, filter_spec, field, partial):
        return dispatch_help_by_field_name(
            self, company, filter_spec, field, partial)

    def help_city(self, company, filter_spec, partial):
        """Get help for the city field."""
        modified_filter_spec = filter_spec.clone_without_city()
        partners_qs = modified_filter_spec.filter_partners(company)
        locations_qs = (
            Location.objects
            .filter(contacts__partner__in=partners_qs)
            .filter(city__icontains=partial))
        city_qs = locations_qs.values('city').distinct()
        return [{'value': c['city'], 'display': c['city']} for c in city_qs]

    def help_state(self, company, filter_spec, partial):
        """Get help for the state field."""
        modified_filter_spec = filter_spec.clone_without_state()
        partners_qs = modified_filter_spec.filter_partners(company)
        locations_qs = (
            Location.objects
            .filter(contacts__partner__in=partners_qs)
            .filter(state__icontains=partial))
        state_qs = locations_qs.values('state').order_by('state').distinct()
        return [{
            'value': c['state'],
            'display': states[c['state']]
        } for c in state_qs if c['state']]

    def help_tags(self, company, filter_spec, partial):
        """Get help for the tags field."""
        partners_qs = PartnersFilter().filter_partners(company)
        tags_qs = (
            Tag.objects
            .filter(partner__in=partners_qs)
            .filter(name__icontains=partial)
            .values('name', 'hex_color').distinct())
        return [
            {
                'value': t['name'],
                'display': t['name'],
                'hexColor': t['hex_color'],
            } for t in tags_qs]

    def help_uri(self, company, filter_spec, partial):
        """Get help for the uri field."""
        partners_qs = filter_spec.filter_partners(company)

        uris_qs = (
            partners_qs
            .filter(uri__icontains=partial)
            .values('uri').distinct())
        return [{'value': c['uri'], 'display': c['uri']} for c in uris_qs]

    def help_data_source(self, company, filter_spec, partial):
        """Get help for the data_source field."""
        partners_qs = filter_spec.filter_partners(company)

        data_sources_qs = (
            partners_qs
            .filter(data_source__icontains=partial)
            .values('data_source').distinct())
        return [
            {'value': c['data_source'], 'display': c['data_source']}
            for c in data_sources_qs
        ]

    def adorn_filter_items(self, company, found_filter_items):
        adorned = {}
        empty = PartnersFilter()

        if 'tags' in found_filter_items:
            adorned[u'tags'] = {
                found['value']: found
                for found in [
                    result
                    for result in self.help_tags(company, empty, '')
                ]
            }

        return adorned

    def get_default_filter(self, data_type, company):
        filter_spec = PartnersFilter(
            date=DateRangeFilter([datetime(2014, 1, 1), datetime.now()]))
        adorned = adorn_filter(company, self, filter_spec)
        return adorned


@dict_identity
class PartnersFilter(DataSourceFilter):
    def __init__(self, date=NoFilter(), locations=NoFilter(), tags=NoFilter(),
                 data_source=NoFilter(), uri=NoFilter()):
        self.date = date
        self.locations = locations
        self.tags = tags
        self.data_source = data_source
        self.uri = uri

    @classmethod
    def filter_key_types(self):
        return {
            'date': 'date_range',
            'locations': 'composite',
        }

    def clone_without_city(self):
        """City help needs it's filter cleared before searching for help.

        Return a new PartnersFilter without the current city filter applied.
        """
        new_root = dict(self.__dict__)
        locations = new_root.get('locations', NoFilter())
        if locations:
            new_locations = dict(locations.field_map)
            if 'city' in locations.field_map:
                del new_locations['city']
            new_root['locations'] = CompositeAndFilter(new_locations)
        return PartnersFilter(**new_root)

    def clone_without_state(self):
        """State help needs it's filter cleared before searching for help.

        Return a new PartnersFilter without the current state filter applied.
        """
        new_root = dict(self.__dict__)
        locations = new_root.get('locations', NoFilter())
        if locations:
            new_locations = dict(locations.field_map)
            if 'state' in locations.field_map:
                del new_locations['state']
            new_root['locations'] = CompositeAndFilter(new_locations)
        return PartnersFilter(**new_root)

    def filter_partners(self, company):
        qs = Partner.objects.filter(owner=company)
        qs = (
            qs
            .filter(approval_status__code__iexact=Status.APPROVED)
            .filter(archived_on__isnull=True))

        qs = apply_filter_to_queryset(
            qs,
            self.date,
            'last_action_time')

        qs = apply_filter_to_queryset(
            qs,
            self.data_source,
            'data_source__iexact')

        qs = apply_filter_to_queryset(
            qs,
            self.uri,
            'uri__iexact')

        qs = apply_filter_to_queryset(
            qs,
            self.tags,
            'tags', '__name__iexact')

        if self.locations:
            contact_qs = Contact.objects.all()

            contact_qs = apply_filter_to_queryset(
                contact_qs,
                self.locations,
                {
                    'city': 'locations__city__iexact',
                    'state': 'locations__state__iexact',
                })

            contact_qs.distinct()
            qs = qs.filter(primary_contact=contact_qs)

        return qs
