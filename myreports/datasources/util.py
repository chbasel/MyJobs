from operator import __or__, __and__
from django.db.models import Q
from datetime import timedelta
from universal.helpers import dict_identity


def dispatch_help_by_field_name(ds, company, filter_spec, field, partial):
    """Invoke ds.help_[field] method.

    example:
        given field='city':
        return ds.help_city(company, filter_spec, partial)

    Breaks up large help methods into smaller help methods separated by field
    name.

    signatures of help_[field] should match the signature of
    DataSource.help without the field parameter.
    """
    method = getattr(ds, 'help_' + field)
    return method(company, filter_spec, partial)


def dispatch_run_by_data_type(ds, data_type, company, filter_spec, order_spec):
    """Invoke ds.run_[date_type] method.

    example:
        given data_type='partner_per_month':
        return ds.run_partner_per_month(company, filter_spec, order_spec)

    Breaks up large run methods into smaller run methods separated by
    data_type.

    signatures of run_[data_type] should match the signature of
    DataSource.run without the data_type parameter.
    """
    method = getattr(ds, 'run_' + data_type)
    return method(company, filter_spec, order_spec)


def build_q(field, op, data):
    return Q(**{field + '__' + op: data})


def extract_tags(tag_list):
    """Extract name + hex_color + ... from tags."""
    return [
        {
            'id': t.id,
            'name': t.name,
            'hex_color': t.hex_color,
        }
        for t in tag_list.all()
    ]


def apply_filter_to_queryset(queryset, filt, field, extension=None):
    """
    Apply the given filter to the given queryset using the provided field info.

    queryset: a queryset to apply the filter to
    filt: a filter object
    field: base field name.
    extension: rest of field name

    Special cases:
        CompositeAndFilter: field is a dictionary of field info: i.e. {
            'name': 'name__iexact,
        }
        UnlinkedFilter uses only field, not field+extension as the field to
            compare. i.e.

            apply_filter_to_queryset(qs, filt, 'tags', '__name__iexact')

            This works for ordinary filters, which use field+exention. If
            filt is UnlinkedFilter we still get the expected behavior since
            bare field is what we need to compare against None.
    """
    if extension:
        full_field = field + extension
    else:
        full_field = field

    result = queryset

    # and'ed Q won't work as it means something different
    # https://docs.djangoproject.com/en/dev/topics/db/queries/#spanning-multi-valued-relationships
    # So we handle AndGroupFilter at this level only.
    if isinstance(filt, AndGroupFilter):
        for child in filt.child_filters:
            result = apply_filter_to_queryset(result, child, full_field)
    elif isinstance(filt, UnlinkedFilter):
        result = result.filter(**{field: None})
    else:
        q = as_q(filt, full_field)
        if q is not None:
            result = result.filter(q)
    return result


def as_q(filt, field):
    """
    Convert filters to django db Q values.

    Don't call this directly. Use apply_filter_to_queryset instead.
    filt: a filter object
    field: the db field to use for Q values.
    """
    if isinstance(filt, MatchFilter):
        if filt.value is None or filt.value == '':
            return None

        return Q(**{field: filt.value})
    elif isinstance(filt, OrGroupFilter):
        if not filt.child_filters:
            return None

        return reduce(__or__, (as_q(cf, field) for cf in filt.child_filters))
    elif isinstance(filt, DateRangeFilter):
        if filt.dates is None:
            return None

        begin = None
        if (filt.dates[0] is not None):
            begin = filt.dates[0]

        end = None
        if (filt.dates[1] is not None):
            end = filt.dates[1] + timedelta(days=1)

        if (begin is not None and end is not None):
            return build_q(field, 'range', (begin, end))
        elif end is not None:
            return build_q(field, 'lte', end)
        elif begin is not None:
            return build_q(field, 'gte', begin)
        return None
    elif isinstance(filt, CompositeAndFilter):
        db_field_map = field
        usable_fields = {
            k: v
            for k, v in {
                k: as_q(v, db_field_map[k])
                for k, v in filt.field_map.iteritems()
                if k in db_field_map
            }.iteritems()
            if v is not None
        }

        if not usable_fields:
            return None

        return reduce(__and__, (q for q in usable_fields.itervalues()))
    elif isinstance(filt, NoFilter):
        return None
    else:
        raise KeyError("Can't generate Q for filter: " + str(filt))


def plain_filter(full_filter):
    """
    Convert a filter object back to object form.

    See DataSourceJsonDriver.build_filter for the format.
    """
    return {
        k: reduce_filter(v)
        for k, v in full_filter.__dict__.iteritems()
        if v
    }


def reduce_filter(filt):
    """
    Convert an individual filter to object form.

    Don't call this directly. Call plain_filter instead.
    """
    if isinstance(filt, MatchFilter):
        return filt.value
    elif isinstance(filt, OrGroupFilter):
        # TODO: Note that OrGroupFilter and AndGroupFilter are identical.
        # In the future make these distinct.
        return [
            reduce_filter(f)
            for f in filt.child_filters
        ]
    elif isinstance(filt, AndGroupFilter):
        return [
            reduce_filter(f)
            for f in filt.child_filters
        ]
    elif isinstance(filt, CompositeAndFilter):
        return {
            k: reduce_filter(v)
            for k, v in filt.field_map.iteritems()
        }
    elif isinstance(filt, DateRangeFilter):
        return filt.dates
    elif isinstance(filt, UnlinkedFilter):
        return {'nolink': True}
    else:
        return filt


@dict_identity
class AndGroupFilter(object):
    """
    Represents a series of filters that must all pass.
    """
    def __init__(self, child_filters):
        self.child_filters = child_filters


# TODO: Eliminate this! It is inconsistent with the other fields. It is
# currently only used by city/state fields. A viable strategy is to replace
# the composite fields with separate city and state fields and "blend" them
# in the UI somehow.
@dict_identity
class CompositeAndFilter(object):
    """
    Represents a series of filters on different fields.
    """
    def __init__(self, field_map):
        self.field_map = field_map


@dict_identity
class OrGroupFilter(object):
    """
    Represents a series of filters, any of which should pass.
    """
    def __init__(self, child_filters):
        self.child_filters = child_filters


@dict_identity
class MatchFilter(object):
    """
    Represents a match condition.
    """
    def __init__(self, value):
        self.value = value


@dict_identity
class DateRangeFilter(object):
    """
    Represents a date range.
    """
    def __init__(self, dates):
        self.dates = dates


@dict_identity
class UnlinkedFilter(object):
    """
    Represents the lack of relationship, i.e. untagged.
    """
    pass


@dict_identity
class NoFilter(object):
    """
    Placeholder meaning not filtered.
    """
    def __nonzero__(self):
        return False


def adorn_filter(company, datasource, full_filter):
    """
    Create a new filter matching the old one where MatchFilter's are "adorned".

    Adorning means replacing values like 3 with objects shaped like:
        {value: 3, display: "EmployCo", ... }
    """
    collected = {
        k: collect_matches(f)
        for k, f in full_filter.__dict__.iteritems()
        if f
    }
    adorned_items = datasource.adorn_filter_items(company, collected)

    adorned_filter_dict = {
        k: place_adornments(f, adorned_items.get(k, {}))
        for k, f in full_filter.__dict__.iteritems()
        if f
    }

    return datasource.filter_type()(**adorned_filter_dict)


def collect_matches(filt):
    """
    Find all the values which the datasource needs to provide displays for.
    """
    if isinstance(filt, MatchFilter):
        return [filt.value]
    elif isinstance(filt, OrGroupFilter) or isinstance(filt, AndGroupFilter):
        return [
            item for sublist in [
                collect_matches(f)
                for f in filt.child_filters
            ]
            for item in sublist
        ]
    elif isinstance(filt, CompositeAndFilter):
        return {
            k: collect_matches(f)
            for k, f in filt.field_map.iteritems()
        }
    else:
        return filt


def place_adornments(filt, adorned_items):
    """
    Walk the filter and replace values with display objects where we can.
    """
    if isinstance(filt, MatchFilter):
        return MatchFilter(adorned_items.get(filt.value, filt.value))
    elif isinstance(filt, OrGroupFilter):
        return OrGroupFilter([
            place_adornments(f, adorned_items)
            for f in filt.child_filters
        ])
    elif isinstance(filt, AndGroupFilter):
        return AndGroupFilter([
            place_adornments(f, adorned_items)
            for f in filt.child_filters
        ])
    elif isinstance(filt, CompositeAndFilter):
        adorned_field_map = {
            k: place_adornments(f, adorned_items[k])
            for k, f in filt.field_map.iteritems()
            if k in adorned_items
        }
        merged_field_map = dict(filt.field_map)
        merged_field_map.update(adorned_field_map)
        return CompositeAndFilter(merged_field_map)
    else:
        return filt
