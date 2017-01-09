"""Contacts DataSource"""
from datetime import datetime

from myreports.datasources.util import (
    dispatch_help_by_field_name, dispatch_run_by_data_type,
    extract_tags, adorn_filter,
    apply_filter_to_queryset,
    NoFilter, CompositeAndFilter, DateRangeFilter)
from myreports.datasources.base import DataSource, DataSourceFilter

from mypartners.models import Contact, Location, Tag, Partner, Status

from universal.helpers import dict_identity, extract_value

from postajob.location_data import states


class ContactsDataSource(DataSource):
    def run(self, data_type, company, filter_spec, values):
        return dispatch_run_by_data_type(
            self, data_type, company, filter_spec, values)

    def run_unaggregated(self, company, filter_spec, values):
        """Run the query with the given company, filter, and values.

        returns: list of relatively flat dictionaries.

        The dictionaries have depth only for locations and tags. This is to
        allow for some flexibility in formatting at report download time.
        """
        qs_filtered = self.filtered_query_set(company, filter_spec)
        qs_distinct = qs_filtered.distinct()
        return [self.extract_record(r, values) for r in qs_distinct]

    def filter_type(self):
        return ContactsFilter

    def help(self, company, filter_spec, field, partial):
        return dispatch_help_by_field_name(
            self, company, filter_spec, field, partial)

    def help_city(self, company, filter_spec, partial):
        """Get help for the city field."""
        modified_filter_spec = filter_spec.clone_without_city()
        contacts_qs = self.filtered_query_set(company, modified_filter_spec)
        locations_qs = (
            Location.objects
            .filter(contacts__in=contacts_qs)
            .filter(city__icontains=partial))
        city_qs = locations_qs.values('city').distinct()
        return [{'value': c['city'], 'display': c['city']} for c in city_qs]

    def help_state(self, company, filter_spec, partial):
        """Get help for the state field."""
        modified_filter_spec = filter_spec.clone_without_state()
        contacts_qs = self.filtered_query_set(company, modified_filter_spec)
        locations_qs = (
            Location.objects
            .filter(contacts__in=contacts_qs)
            .filter(state__icontains=partial))
        state_qs = locations_qs.values('state').order_by('state').distinct()
        return [{
            'value': s['state'],
            'display': states[s['state']]
        } for s in state_qs if s['state']]

    def help_tags(self, company, filter_spec, partial):
        """Get help for the tags field."""
        contacts_qs = self.filtered_query_set(company, ContactsFilter())
        tags_qs = (
            Tag.objects
            .filter(contact__in=contacts_qs)
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
        contacts_qs = self.filtered_query_set(company, ContactsFilter())

        partner_qs = Partner.objects.filter(
            contact__in=contacts_qs)
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

    def help_partner(self, company, filter_spec, partial):
        """Get help for the partner field."""
        modified_filter_spec = filter_spec.clone_without_partner()
        contacts_qs = self.filtered_query_set(company, modified_filter_spec)
        partners_qs = (
            Partner.objects
            .filter(contact__in=contacts_qs)
            .filter(name__icontains=partial)
            .values('name', 'pk').distinct())
        return [{'value': t['pk'], 'display':t['name']} for t in partners_qs]

    def extract_record(self, record, values):
        """Translate from a query set record to a dictionary."""
        fields = {
            'name': lambda r: r.name,
            'partner': lambda r: extract_value(r, 'partner', 'name'),
            'email': lambda r: r.email,
            'phone': lambda r: r.phone,
            'notes': lambda r: r.notes,
            'locations': lambda r: [
                {'city': l.city, 'state': l.state}
                for l in r.locations.all()
            ],
            'date': lambda r: r.last_action_time,
            'tags': lambda r: extract_tags(r.tags.all()),
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

    def filtered_query_set(self, company, filter_spec):
        """Create a query set with security, safety, and user filters applied.
        """
        qs_company = Contact.objects.filter(partner__owner=company)
        qs_live = (
            qs_company
            .filter(approval_status__code__iexact=Status.APPROVED)
            .filter(partner__approval_status__code__iexact=Status.APPROVED)
            .filter(archived_on__isnull=True))
        qs_filtered = filter_spec.filter_query_set(qs_live)
        return qs_filtered

    def adorn_filter_items(self, company, found_filter_items):
        adorned = {}
        empty = ContactsFilter()

        if 'tags' in found_filter_items:
            adorned[u'tags'] = {
                found['value']: found
                for found in [
                    result
                    for result in self.help_tags(company, empty, '')
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

        return adorned

    def get_default_filter(self, data_type, company):
        filter_spec = ContactsFilter(
            date=DateRangeFilter([datetime(2014, 1, 1), datetime.now()]))
        adorned = adorn_filter(company, self, filter_spec)
        return adorned


@dict_identity
class ContactsFilter(DataSourceFilter):
    """Represent a ContactsDataSource user filter."""
    def __init__(self, date=NoFilter(), locations=NoFilter(), tags=NoFilter(),
                 partner=NoFilter(), partner_tags=NoFilter()):
        self.date = date
        self.locations = locations
        self.tags = tags
        self.partner = partner
        self.partner_tags = partner_tags

    @classmethod
    def filter_key_types(self):
        return {
            'date': 'date_range',
            'locations': 'composite',
        }

    def clone_without_city(self):
        """City help needs it's filter cleared before searching for help.

        Return a new ContactsFilter without the current city filter applied.
        """
        new_root = dict(self.__dict__)
        locations = new_root.get('locations', NoFilter())
        if locations:
            new_locations = dict(locations.field_map)
            if 'city' in locations.field_map:
                del new_locations['city']
            new_root['locations'] = CompositeAndFilter(new_locations)
        return ContactsFilter(**new_root)

    def clone_without_state(self):
        """State help needs it's filter cleared before searching for help.

        Return a new ContactsFilter without the current state filter applied.
        """
        new_root = dict(self.__dict__)
        locations = new_root.get('locations', None)
        if locations:
            new_locations = dict(locations.field_map)
            if 'state' in locations.field_map:
                del new_locations['state']
            new_root['locations'] = CompositeAndFilter(new_locations)
        return ContactsFilter(**new_root)

    def clone_without_partner(self):
        """Partner help should not self filter."""
        new_root = dict(self.__dict__)
        del new_root['partner']
        return ContactsFilter(**new_root)

    def filter_query_set(self, qs):
        """Apply the filter described by this instance to a query set.

        qs: the query set to receive the filter
        """
        qs = apply_filter_to_queryset(
            qs,
            self.date,
            'last_action_time')

        qs = apply_filter_to_queryset(
            qs,
            self.tags,
            'tags', '__name__iexact')

        qs = apply_filter_to_queryset(
            qs,
            self.locations,
            {
                'city': 'locations__city__iexact',
                'state': 'locations__state__iexact',
            })

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
