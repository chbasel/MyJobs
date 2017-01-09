import json
from datetime import datetime

from myreports.datasources.util import (
    plain_filter, adorn_filter,
    AndGroupFilter, CompositeAndFilter, OrGroupFilter, MatchFilter,
    DateRangeFilter, UnlinkedFilter)


class DataSourceJsonDriver(object):
    def __init__(self, ds):
        self.ds = ds

    def run(self, data_type, company, filter_spec, values_spec):
        """Run the report.

        data_type: name of query variant, i.e. unaggregated, per_year
        company: company model object for this run.
        filter_spec: string with json object representing the user filter
        value_spec: string with json list of fields to include

        returns: list of relatively flat dictionaries.
        """
        return self.ds.run(
            data_type,
            company,
            self.build_filter(filter_spec),
            self.build_values(values_spec))

    def help(self, company, filter_spec, field, partial):
        """Get help values for a particular field.

        company: company model object for this run.
        filter_spec: string with json object for the current user filter.
        field: which field we are getting help for
        partial: the user input in the field so far
        """
        filter_obj = self.build_filter(filter_spec)
        return self.ds.help(company, filter_obj, field, partial)

    def adorn_filter(self, company, filter_spec):
        """Get a version of the filter help added where available.

        company: company model object for this run.
        filter_spec: string with json object for the current user filter.

        returns:
            a json object shaped like filter_spec
            values on fields with help available will be replaced with help
        """
        filter_obj = self.build_filter(filter_spec)
        return plain_filter(adorn_filter(company, self.ds, filter_obj))

    def get_default_filter(self, data_type, company):
        """Get a filter object with default values prepopulated.

        data_type: name of query variant, i.e. unaggregated, per_year
        company: company model object for this run.

        returns:
            an adorned filter with default values
            see adorn_filter
        """
        return plain_filter(self.ds.get_default_filter(data_type, company))

    def build_order(self, order_spec):
        """Build a list of order_by fields from the given order_spec."""
        return json.loads(order_spec)

    def build_values(self, values_spec):
        """Build a list of fields from the given values_spec."""
        return json.loads(values_spec)

    def build_filter(self, filter_json):
        """
        Build a filter for the given filter_json

        filters look like: {
            filter_column1: some filter_spec...,
            filter_column2: another filter_spec...,

        }

        filter_specs can be any of:

        missing/null/[]: Empty lists, nulls, or missing keys are all
            interpreted as do not filter on this column.

        [date, date]: A list of two dates is date range. The filter
            class must have a key type of 'date'.

        1/"a": A single choice.

        [1, 2, 3]: A list of choices is an "or group". Match any of the
            choices.

        [[1, 2, 3], [4, 5, 6]]: A list of lists of choices is an "and group".
            Must match any of the first AND any of each of the subsequent
            groups.

        {'field1': some filter}: Match each field with the filter given:
            A CompositeAndFilter. The filter class must have a key type of
            'composite'.

        {'nolink': True}: A special object which means to find objects not
            linked to the objects in this column. i.e. If this is a tags
            column, find untagged objects.
        """
        kwargs = {}
        filter_spec = json.loads(filter_json)
        filter_type = self.ds.filter_type()
        types = filter_type.filter_key_types()
        for key, data in filter_spec.iteritems():
            key_type = types.get(key, None)
            if key_type is None:
                # empty lists are the same as no filter
                if data == []:
                    continue

                elif (isinstance(data, list) and
                        len(data) > 0 and
                        isinstance(data[0], list)):
                    kwargs[key] = AndGroupFilter([
                        OrGroupFilter([
                            MatchFilter(v)
                            for v in or_f
                            ])
                        for or_f in data])

                elif isinstance(data, list) and len(data) > 0:
                    kwargs[key] = OrGroupFilter([
                        MatchFilter(v)
                        for v in data
                        ])

                elif isinstance(data, dict) and 'nolink' in data:
                    kwargs[key] = UnlinkedFilter()

                else:
                    kwargs[key] = MatchFilter(data)

            elif key_type == 'date_range':
                date_strings = filter_spec.get(key, None)
                dates = [
                    (datetime.strptime(d, "%m/%d/%Y") if d else None)
                    for d in date_strings]

                kwargs[key] = DateRangeFilter(dates)

            elif key_type == 'composite':
                value_map = {
                    col: MatchFilter(value)
                    for col, value in filter_spec.get(key, {}).iteritems()
                }

                kwargs[key] = CompositeAndFilter(value_map)

            else:
                message = 'DataSource %s has unknown filter key type %s' % (
                    self.ds.__class__.__name__,
                    repr(key_type))
                raise KeyError(message)

        return filter_type(**kwargs)

    def serialize_filterlike(self, filterlike):
        """Serialize raw python data to JSON. Including datetime, etc."""
        return json.dumps(filterlike, cls=CustomEncoder)

    def encode_filter_interface(self, report_configuration):
        """Describe the filter_interface in python primitives.

        Output is suitable for serializing to JSON.
        """
        column_configs = report_configuration.columns
        filters = [
            self.encode_single_filter_interface(c)
            for c in column_configs
            if c.filter_interface is not None
        ]

        help_available = dict(
            (c.column, True)
            for c in column_configs
            if c.help)

        return {
            'filters': filters,
            'help': help_available,
        }

    def encode_single_filter_interface(self, column_config):
        return {
            'interface_type': column_config.filter_interface,
            'filter': column_config.column,
            'display': column_config.filter_display,
        }


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%m/%d/%Y')
        return json.JSONEncoder.default(self, obj)
