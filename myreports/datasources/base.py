from abc import ABCMeta, abstractmethod


class DataSource:
    """A queryable datasource.

        class SomeDataSource(DataSource):
            def filter_type(self):
                return SomeFilter # See DataSourceFilter

            def run(self, company, filter_spec, order):
                ...

            def help(self, company, filter_spec, field, partial):
                ...

    Instances can run queries on behalf of users, as well as provide help
    in constructing useful filters for those queries.

    The queries are not aware of particular users. This protocol just
    requires a company to limit results.

    Classes derived from this base also require a companion filter class
    derived from DataSourceFilter.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def filter_type(self):
        """Return the companion filter type for this class.

        The companion type should be derived from DataSourceFilter.
        """
        raise NotImplementedError(
            "Missing filter_type method on this instance.")

    @abstractmethod
    def run(self, data_type, company, filter_spec, values_spec):
        """Run the query with the given company, filter, and values.

        data_type: data_type variant to run; i.e. unaggregated, per_year
        company: reference to the company for the logged in user
        filter_spec: an instance of the companion filter type for this class.
        values_spec: a list of fields to include in the query result

        returns: list of relatively flat dictionaries.

        The dictionaries have some depth at this point. This is to allow for
        some flexibility in formatting at report download time.
        """
        raise NotImplementedError("Missing run method on this instance.")

    @abstractmethod
    def help(self, company, filter_spec, field, partial):
        """Get help for the given field.

        company: reference to the company for the logged in user
        filter_spec: an instance of the companion filter type for this class.
        field: the name of the field we are getting help for.
        partial: the input given by the user so far.

        returns: list of dictionaries in the form:
            { value: 'value', display: 'Display String', ...}

        This is used to list of possible completions for given user input in
        a form useful to filter building UI.

        The UI is expected do display the display value, but provide the key
        value as part of filter_spec when running the query.
        """
        raise NotImplementedError("Missing help method on this instance.")

    @abstractmethod
    def adorn_filter_items(self, company, found_items):
        """Get a version of the filter with help added where available.

        company: company model object for this run.
        found_items: a dict of values found in the filter
            e.g. {
                'tags': ['east', 'west'],
                'partner': [2, 5],
            }


        returns:
            a dict of dicts of {value/display} objects for the ids given
            in found_filter.
            e.g. {
                'tags': {
                    'east': {'value': 'east', 'display': ... },
                    'west': {'value': 'west', 'display': ... },
                }, ...
            }
        """
        raise NotImplementedError("Missing adorn_filter_items method.")


class DataSourceFilter:
    """A filter on a query for an DataSource, populated with values.

        class SomeFilter(DataSource):
            def __init__(
                dates,
                city):
                self.dates = dates
                self.city = city

            @classmethod
            def filter_key_types(self):
                return {'dates': 'date_range'}

            def clone_without_city(self):
                new_data = dict(self.__dict__)
                new_data['city'] = None
                return SomeFilter(**new_data)

            def filter_query_set(self, query_set):
                ...

    An instance should be handled like an immutable value. All values
    pertaining to the filter should be provided to the constructor. If a
    variation of an existing filter is needed, add "clone_*" methods to the
    derived class.

    i.e. clone_without_city(self) would return a new instance of the class
    with the city instance variable set to None.

    Derived instances should also provide a @classmethod called
    filter_key_types. This provides a signal to DataSourceJsonDriver that
    it should do extra parsing on the json data for that field.
    """
    __metaclass__ = ABCMeta
