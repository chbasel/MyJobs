"""CommRecords DataSource"""
from HTMLParser import HTMLParser
from datetime import datetime

from django.utils.html import strip_tags

from mypartners.models import (
    Contact, Status, Location, Tag, ContactRecord, Partner)

from postajob.location_data import states

from myreports.datasources.util import (
    dispatch_help_by_field_name, dispatch_run_by_data_type,
    extract_tags, adorn_filter,
    apply_filter_to_queryset,
    NoFilter, CompositeAndFilter, DateRangeFilter)
from myreports.datasources.base import DataSource, DataSourceFilter

from universal.helpers import dict_identity, extract_value
from mypartners.models import CONTACT_TYPE_CHOICES


CONTACT_TYPES = dict(CONTACT_TYPE_CHOICES)


def contact_type_help_entry(contact_type):
    value = contact_type.lower()
    display = CONTACT_TYPES[value]
    return {'value': value, 'display': display}


class CommRecordsDataSource(DataSource):
    def run(self, data_type, company, filter_spec, values):
        return dispatch_run_by_data_type(
            self, data_type, company, filter_spec, values)

    def run_unaggregated(self, company, filter_spec, values):
        qs_filtered = self.filtered_query_set(company, filter_spec)
        qs_distinct = qs_filtered.distinct()
        return [self.extract_record(r, values) for r in qs_distinct]

    def extract_record(self, record, values):
        fields = {
            'contact': lambda r: extract_value(r, 'contact', 'name'),
            'contact_email': lambda r: r.contact_email,
            'contact_phone': lambda r: r.contact_phone,
            'communication_type': lambda r: r.contact_type,
            'created_on': lambda r: r.created_on,
            'created_by': lambda r: extract_value(r, 'created_by', 'email'),
            'date_time': lambda r: r.date_time,
            'job_applications': lambda r: r.job_applications,
            'job_hires': lambda r: r.job_hires,
            'job_id': lambda r: r.job_id,
            'job_interviews': lambda r: r.job_interviews,
            'last_action_time': lambda r: r.last_action_time,
            'length': lambda r: r.length,
            'location': lambda r: r.location,
            'notes': lambda r: self.normalize_html(r.notes),
            'partner': lambda r: extract_value(r, 'partner', 'name'),
            'subject': lambda r: r.subject,
            'tags': lambda r: extract_tags(r.tags),
        }

        if values:
            return_values = values
        else:
            return_values = fields.keys()

        return {
            k: v(record)
            for k, v in fields.iteritems()
            if k in return_values
        }

    def normalize_html(self, html):
        """Strip HTML Tags and normalize gratuitous newlines."""

        parser = HTMLParser()
        results = parser.unescape(
            '\n'.join(' '.join(line.split())
                      for line in strip_tags(html).splitlines() if line))

        return '\n'.join(filter(bool, results.split('\n\n')))

    def filter_type(self):
        return CommRecordsFilter

    def help(self, company, filter_spec, field, partial):
        return dispatch_help_by_field_name(
            self, company, filter_spec, field, partial)

    def help_city(self, company, filter_spec, partial):
        """Get help for the city field."""
        modified_filter_spec = filter_spec.clone_without_city()
        comm_records_qs = self.filtered_query_set(
            company, modified_filter_spec)
        locations_qs = (
            Location.objects
            .filter(contacts__contactrecord__in=comm_records_qs)
            .filter(city__icontains=partial))
        city_qs = locations_qs.values('city').distinct()
        return [{'value': c['city'], 'display': c['city']} for c in city_qs]

    def help_state(self, company, filter_spec, partial):
        """Get help for the state field."""
        modified_filter_spec = filter_spec.clone_without_state()
        comm_records_qs = self.filtered_query_set(
            company, modified_filter_spec)
        locations_qs = (
            Location.objects
            .filter(contacts__contactrecord__in=comm_records_qs)
            .filter(state__icontains=partial))
        state_qs = locations_qs.values('state').order_by('state').distinct()
        return [{
            'value': c['state'],
            'display': states[c['state']]
        } for c in state_qs if c['state']]

    def help_tags(self, company, filter_spec, partial):
        """Get help for the tags field."""
        comm_records_qs = self.filtered_query_set(company, CommRecordsFilter())

        tags_qs = (
            Tag.objects
            .filter(contactrecord__in=comm_records_qs)
            .filter(name__icontains=partial)
            .values('name', 'hex_color').distinct())
        return [
            {
                'value': t['name'],
                'display': t['name'],
                'hexColor': t['hex_color'],
            } for t in tags_qs]

    def help_contact_tags(self, company, filter_spec, partial):
        """Get help for the contact tags field."""
        comm_records_qs = self.filtered_query_set(company, CommRecordsFilter())

        contact_qs = Contact.objects.filter(contactrecord__in=comm_records_qs)
        tags_qs = (
            Tag.objects
            .filter(contact__in=contact_qs)
            .filter(name__icontains=partial)
            .values('name', 'hex_color').distinct())
        return [
            {
                'value': t['name'],
                'display': t['name'],
                'hexColor': t['hex_color'],
            } for t in tags_qs]

    def help_partner_tags(self, company, filter_spec, partial):
        """Get help for the partner tags field."""
        comm_records_qs = self.filtered_query_set(company, CommRecordsFilter())

        partner_qs = Partner.objects.filter(
            contact__contactrecord__in=comm_records_qs)
        tags_qs = (
            Tag.objects
            .filter(partner__in=partner_qs)
            .filter(name__icontains=partial)
            .values('name', 'hex_color').distinct())
        return [
            {
                'value': t['name'],
                'display': t['name'],
                'hexColor': t['hex_color'],
            } for t in tags_qs]

    def help_communication_type(self, company, filter_spec, partial):
        """Get help for the communication type field."""
        return [
            contact_type_help_entry(c[0])
            for c in CONTACT_TYPE_CHOICES]

    def help_partner(self, company, filter_spec, partial):
        """Get help for the partner field."""
        # Don't let this help be dependent on filtered contacts.
        modified_filter_spec = (
            filter_spec.clone_without_contact().clone_without_partner())
        comm_records_qs = self.filtered_query_set(
            company, modified_filter_spec)
        partner_qs = (
            Partner.objects
            .filter(name__icontains=partial)
            .filter(contactrecord__in=comm_records_qs)
            .values('pk', 'name').distinct())
        return [
            {
                'value': c['pk'],
                'display': c['name'],
            } for c in partner_qs]

    def help_contact(self, company, filter_spec, partial):
        """Get help for the contact field."""
        modified_filter_spec = filter_spec.clone_without_contact()
        comm_records_qs = self.filtered_query_set(
            company, modified_filter_spec)
        contact_qs = (
            Contact.objects
            .filter(name__icontains=partial)
            .filter(contactrecord__in=comm_records_qs)
            .values('pk', 'name').distinct())
        return [
            {
                'value': c['pk'],
                'display': c['name'],
            } for c in contact_qs]

    def filtered_query_set(self, company, filter_spec):
        """Create a query set with security, safety, and user filters applied.
        """
        qs_company = ContactRecord.objects.filter(partner__owner=company)
        qs_live = (
            qs_company
            .filter(approval_status__code__iexact=Status.APPROVED)
            .filter(archived_on__isnull=True))
        qs_filtered = filter_spec.filter_query_set(qs_live)
        qs_optimized = (
            qs_filtered.prefetch_related('contact')
            .prefetch_related('partner')
            .prefetch_related('created_by')
            .prefetch_related('tags'))
        return qs_optimized

    def adorn_filter_items(self, company, found_filter_items):
        adorned = {}
        empty = CommRecordsFilter()

        if 'tags' in found_filter_items:
            adorned[u'tags'] = {
                found['value']: found
                for found in [
                    result
                    for result in self.help_tags(company, empty, '')
                ]
            }

        if 'contact_tags' in found_filter_items:
            adorned[u'contact_tags'] = {
                found['value']: found
                for found in [
                    result
                    for result in self.help_contact_tags(company, empty, '')
                ]
            }

        if 'partner_tags' in found_filter_items:
            adorned[u'partner_tags'] = {
                found['value']: found
                for found in [
                    result
                    for result in self.help_partner_tags(company, empty, '')
                ]
            }

        if 'partner' in found_filter_items:
            partners_qs = (
                Partner.objects
                .filter(owner=company)
                .filter(pk__in=found_filter_items['partner'])
                .values('name', 'pk').distinct())

            adorned[u'partner'] = {
                found['value']: found
                for found in [
                    {'value': p['pk'], 'display': p['name']}
                    for p in partners_qs
                ]
            }

        if 'contact' in found_filter_items:
            contacts_qs = (
                Contact.objects
                .filter(partner__owner=company)
                .filter(pk__in=found_filter_items['contact'])
                .values('name', 'pk').distinct())

            adorned[u'contact'] = {
                found['value']: found
                for found in [
                    {'value': p['pk'], 'display': p['name']}
                    for p in contacts_qs
                ]
            }

        if 'communication_type' in found_filter_items:
            adorned[u'communication_type'] = {
                contact_type_help_entry(c)['value']: contact_type_help_entry(c)
                for c in found_filter_items['communication_type']
            }

        return adorned

    def get_default_filter(self, data_type, company):
        filter_spec = CommRecordsFilter(
            date_time=DateRangeFilter([datetime(2014, 1, 1), datetime.now()]))
        adorned = adorn_filter(company, self, filter_spec)
        return adorned


@dict_identity
class CommRecordsFilter(DataSourceFilter):
    def __init__(self, date_time=NoFilter(), locations=NoFilter(),
                 tags=NoFilter(), communication_type=NoFilter(),
                 partner=NoFilter(), contact=NoFilter(),
                 contact_tags=NoFilter(), partner_tags=NoFilter()):
        self.date_time = date_time
        self.locations = locations
        self.tags = tags
        self.communication_type = communication_type
        self.partner = partner
        self.contact = contact
        self.contact_tags = contact_tags
        self.partner_tags = partner_tags

    @classmethod
    def filter_key_types(self):
        return {
            'date_time': 'date_range',
            'locations': 'composite',
        }

    def clone_without_city(self):
        """City help needs it's filter cleared before searching for help.

        Return a new CommRecordsFilter without the current city filter applied.
        """
        new_root = dict(self.__dict__)
        locations = new_root.get('locations', NoFilter())
        if locations:
            new_locations = dict(locations.field_map)
            if 'city' in locations.field_map:
                del new_locations['city']
            new_root['locations'] = CompositeAndFilter(new_locations)
        return CommRecordsFilter(**new_root)

    def clone_without_state(self):
        """State help needs it's filter cleared before searching for help.

        Return a new CommRecordsFilter without the current state filter
        applied.
        """
        new_root = dict(self.__dict__)
        locations = new_root.get('locations', NoFilter())
        if locations:
            new_locations = dict(locations.field_map)
            if 'state' in locations.field_map:
                del new_locations['state']
            new_root['locations'] = CompositeAndFilter(new_locations)
        return CommRecordsFilter(**new_root)

    def clone_without_tags(self):
        """Tag help works better without tags filtering each other right now.
        """
        new_root = dict(self.__dict__)
        del new_root['tags']
        return CommRecordsFilter(**new_root)

    def clone_without_contact(self):
        """Contact help needs to not self filter."""
        new_root = dict(self.__dict__)
        del new_root['contact']
        return CommRecordsFilter(**new_root)

    def clone_without_partner(self):
        """Partner help needs to not self filter."""
        new_root = dict(self.__dict__)
        del new_root['partner']
        return CommRecordsFilter(**new_root)

    def filter_query_set(self, qs):
        qs = apply_filter_to_queryset(
            qs,
            self.date_time,
            'date_time')
        qs = apply_filter_to_queryset(
            qs,
            self.communication_type,
            'contact_type')
        qs = apply_filter_to_queryset(
            qs,
            self.tags,
            'tags', '__name__iexact')

        if self.locations or self.contact or self.contact_tags:
            contact_qs = Contact.objects.all()
            contact_qs = apply_filter_to_queryset(
                contact_qs,
                self.locations,
                {
                    'city': 'locations__city__iexact',
                    'state': 'locations__state__iexact',
                })
            contact_qs = apply_filter_to_queryset(
                contact_qs,
                self.contact,
                'pk')
            contact_qs = apply_filter_to_queryset(
                contact_qs,
                self.contact_tags,
                'tags', '__name__iexact')

            contact_qs = contact_qs.distinct()

            qs = qs.filter(contact=contact_qs)

        if self.partner or self.partner_tags:
            partner_qs = Partner.objects.all()

            partner_qs = apply_filter_to_queryset(
                partner_qs,
                self.partner,
                'pk')
            partner_qs = apply_filter_to_queryset(
                partner_qs,
                self.partner_tags,
                'tags', '__name__iexact')

            partner_qs = partner_qs.distinct()

            qs = qs.filter(partner=partner_qs)

        return qs
