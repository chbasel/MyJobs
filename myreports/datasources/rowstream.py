"""Rowstreams for blending Django query sets and raw sql queries.

These utilities provide a common "RowStream" interface to Django query sets
and the results of sql queries.

RowStreams have a fields property and are iterable.

Currently fields is a list of names. This may change to accommodate more
sophisticated presentation types. Types such as int, date, string, etc. may
be needed.

Iterating over a row stream yields dictionaries.
    for row in iter(stream):
        print row
    # i.e.: {'id': 3, 'name': 'Acme Inc.', ...}
"""

from operator import neg


def identity(value):
    """Return the given value. Opposite of operator.neg."""
    return value


class DjangoRowBuilder(object):
    """Adapt a particular Django queryset to RowStream.

    i.e:
        partner_row_builder = DjangoRowBuilder([
            DjangoField('id', rename='partner_id'),
            DjangoField('data_source'),
            DjangoField('last_action_time', rename='date'),
            DjangoField('name'),
            DjangoField('primary_contact.name', rename='primary_contact'),
            DjangoField('tags', transform=extract_tags),
            DjangoField('uri')])


    """
    def __init__(self, django_fields):
        """List of fields available in the row dictionaries."""
        self.django_fields = django_fields

    def limit_fields(self, names):
        """
        Limit fields by this list of fields.

        names: list of field names to return.
            If falsey, return all fields.

        """
        if names:
            return [f for f in self.django_fields if f.get_name() in names]
        else:
            return self.django_fields

    def get_fields(self, fields=None):
        """Field list for this record set."""
        return [f.get_name() for f in self.limit_fields(fields)]

    def get_values(self, record, fields=None):
        """Return a row dictionary."""
        return {
            f.get_name(): f.get_value(record)
            for f in self.limit_fields(fields)}


class DjangoField(object):
    """Describe a particular Django field."""
    def __init__(self, field_name, rename=None, transform=identity):
        """
        field_name: Django's name for the field. Double underscore or dotted
            joins are ok.
        rename: Optional: Name of the field in the row stream.
        transform: Optional: function to run on the value of the field
            before including the value in the row. Needed for many to many
            joins.
        """
        self.field_name = field_name

        self.rename = rename
        self.transform = transform

    def get_value(self, record):
        """Get the value for this field after transforming."""
        names = self.field_name.split('.')
        value = record
        for name in names:
            value = getattr(value, name)
            if value is None:
                break
        return self.transform(value)

    def get_name(self):
        """Get the name for this field after renaming."""
        if self.rename:
            return self.rename
        else:
            return self.field_name


class DjangoRowStream(object):
    def __init__(self, builder, query_set, values=None):
        self.builder = builder
        self.query_set = query_set
        self.values = values

    @property
    def fields(self):
        return self.builder.get_fields(self.values)

    def __iter__(self):
        return (
            self.builder.get_values(r, self.values)
            for r in self.query_set)


def from_django(builder, query_set, values=None):
    """Create a RowStream for this queryset using the given builder."""
    return DjangoRowStream(builder, query_set, values)


class SqlRowStream(object):
    def __init__(self, cursor):
        self.cursor = cursor

    @property
    def fields(self):
        return [f[0] for f in self.cursor.description]

    def __iter__(self):
        return iter(dict(zip(self.fields, r)) for r in self.cursor)


def from_cursor(cursor):
    """Create a RowStream for this MySql cursor.

    Assumes that the query writer has done the work of trimming down to just
    data we are interested in, so returns all fields from the query.

    cursor: a Django wrapped MySql cursor. Might not work with other DBs.
    """
    return SqlRowStream(cursor)


class ListRowStream(object):
    def __init__(self, fields, data):
        self.fields = fields
        self.data = data

    def __iter__(self):
        return iter(self.data)

    def sort(self, comparator):
        self.data.sort(cmp=comparator.cmp)


def from_list(fields, list_of_dicts):
    """Create a RowStream from this list of dictionaries.

    The resulting row stream should be iterable multiple times.

    fields: field list. Row dicts should all contain exactly these fields.
    list_of_dicts: List of row dictionaries. Really should be a list.
    """
    return ListRowStream(fields, list_of_dicts)


class IteratorRowStream(object):
    def __init__(self, fields, iterator):
        self.fields = fields
        self.iterator = iterator

    def __iter__(self):
        return iter(self.iterator)


def from_iter(fields, iter_over_dicts):
    """Create a RowStream from this iterator over a sequence of dictionaries.

    The resulting row stream may not be iterable multiple times.

    fields: field list. Row dicts should all contain exactly these fields.
    iter_over_dicts: Iterator over row dictionaries.
    """
    return IteratorRowStream(fields, iter_over_dicts)


def parse_comparator(order):
    """Build a row comparator from a Django like order list.

    order: a list of fields for ordering like Django's.
        i.e: ['a', 'b'], or ['a', '-b']
    """
    fields = []
    directions = []
    for spec in order:
        field_name = None
        direction = None
        if spec.startswith('-'):
            field_name = spec[1:]
            direction = neg
        else:
            field_name = spec
            direction = identity
        directions.append(direction)
        fields.append(field_name)
    return RowComparator(fields, directions)


class RowComparator(object):
    def __init__(self, fields, directions):
        self.fields = fields
        self.directions = directions

    def cmp(self, row_a, row_b):
        for field, direction in zip(self.fields, self.directions):
            result = direction(cmp(row_a[field], row_b[field]))
            if result:
                return result
        return 0


def sort_stream(order, stream):
    """Sort RowStream records similar to Django.

    order: a list of fields for ordering like Django's.
        i.e: ['a', 'b'], or ['a', '-b']
    stream: a RowStream

    returns: a new RowStream with the records sorted.
    """
    comparator = parse_comparator(order)
    cloned_stream = ListRowStream(stream.fields, list(stream))
    cloned_stream.sort(comparator)
    return cloned_stream
