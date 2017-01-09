from operator import neg
from unittest import TestCase

from myreports.datasources.util import extract_tags
from myreports.datasources.rowstream import (
    DjangoField, DjangoRowBuilder,
    from_django, from_cursor, from_iter,
    RowComparator, identity,
    parse_comparator, sort_stream)


class MockQuerySet(object):
    def __iter__(self):
        return iter([MockRecord()])

    def all(self):
        return self


class MockRecord(object):
    id = 1
    a = 'aa'
    n = None
    name = 'somename'
    hex_color = 'bbccdd'
    tags = MockQuerySet()

    @property
    def contact(self):
        return self


class TestDjangoRowStream(TestCase):
    def test_django_field(self):
        """Simple field extraction works."""
        field = DjangoField('a')
        self.assertEqual('aa', field.get_value(MockRecord()))
        self.assertEqual('a', field.get_name())

    def test_django_dotted_name_field(self):
        """Follow a django dot relation."""
        field = DjangoField('contact.a', rename='c')
        self.assertEqual('aa', field.get_value(MockRecord()))
        self.assertEqual('c', field.get_name())

    def test_django_dotted_name_field_none(self):
        """Recover from None in a dot relation."""
        field = DjangoField('contact.n', rename='n')
        self.assertEqual(None, field.get_value(MockRecord()))
        self.assertEqual('n', field.get_name())

    def test_django_field_rename(self):
        """Rename the Django field in the Row."""
        field = DjangoField('a', rename='b')
        self.assertEqual('aa', field.get_value(MockRecord()))
        self.assertEqual('b', field.get_name())

    def test_django_field_tranform(self):
        """Transform the value in the Django field."""
        field = DjangoField('tags', transform=extract_tags)
        self.assertEqual(
            [{'id': 1, 'name': 'somename', 'hex_color': 'bbccdd'}],
            [dict(r) for r in field.get_value(MockRecord())])

    def test_row_builder(self):
        """Build a row from several DjangoFields."""
        row_builder = DjangoRowBuilder([
            DjangoField('a'),
            DjangoField('a', rename='b'),
            DjangoField('tags', transform=extract_tags)])

        self.assertEqual(['a', 'b', 'tags'], row_builder.get_fields())
        expected_tag_list = [
            {'id': 1, 'name': 'somename', 'hex_color': 'bbccdd'}]
        self.assertEqual(
            {'a': 'aa', 'b': 'aa', 'tags': expected_tag_list},
            row_builder.get_values(MockRecord()))

    def test_row_stream_query_set(self):
        """Build a RowStream from a Django query set."""
        row_builder = DjangoRowBuilder([
            DjangoField('a'),
            DjangoField('a', rename='b')])
        row_stream = from_django(row_builder, MockQuerySet())
        self.assertEqual(['a', 'b'], row_stream.fields)
        self.assertEqual([{'a': 'aa', 'b': 'aa'}], list(row_stream))

    def test_row_stream_limit_fields(self):
        row_builder = DjangoRowBuilder([
            DjangoField('a'),
            DjangoField('name'),
            DjangoField('n')])
        row_stream = from_django(
            row_builder,
            MockQuerySet(),
            values=['a', 'name'])
        self.assertEqual(['a', 'name'], row_stream.fields)
        self.assertEqual([{'a': 'aa', 'name': 'somename'}], list(row_stream))


class MockCursor(object):
    @property
    def description(self):
        return (('a',), ('b',), ('c',))

    def __iter__(self):
        return iter([
            (1, 2, 4),
            (5, 6, 7),
        ])


class TestSqlRowStream(TestCase):
    def test_get_data(self):
        """Build a RowStream from sql results."""
        stream = from_cursor(MockCursor())
        self.assertEqual(['a', 'b', 'c'], stream.fields)
        self.assertEqual(
            [
                {'a': 1, 'b': 2, 'c': 4},
                {'a': 5, 'b': 6, 'c': 7}], list(stream))


class MockRowStream(object):
    fields = ['a', 'b', 'c']

    def __iter__(self):
        return iter([
            {'a': 1, 'b': 2, 'c': 3},
            {'a': 1, 'b': 3, 'c': 4},
            {'a': 2, 'b': 4, 'c': 5},
            {'a': 2, 'b': 5, 'c': 6},
            {'a': 1, 'b': 6, 'c': 7},
        ])


class TestSorting(TestCase):
    def test_compare_rows(self):
        """Compare Rows using different criteria."""
        self.assert_compare(
            -1,
            {'a': 1, 'b': 2},
            {'a': 2, 'b': 1},
            ['a'],
            [identity])
        self.assert_compare(
            1,
            {'a': 1, 'b': 2},
            {'a': 2, 'b': 1},
            ['b'],
            [identity])
        self.assert_compare(
            0,
            {'a': 1, 'b': 2},
            {'a': 1, 'b': 3},
            ['a'],
            [identity])
        self.assert_compare(
            -1,
            {'a': 1, 'b': 2},
            {'a': 1, 'b': 3},
            ['a', 'b'], [identity, identity])
        self.assert_compare(
            1,
            {'a': 1, 'b': 2},
            {'a': 1, 'b': 3},
            ['a', 'b'], [identity, neg])
        self.assert_compare(
            -1,
            {'a': 2, 'b': 1},
            {'a': 3, 'b': 1},
            ['b', 'a'], [identity, identity])
        self.assert_compare(
            1,
            {'a': 1, 'b': 2},
            {'a': 2, 'b': 1},
            ['a'],
            [neg])
        self.assert_compare(
            0,
            {'a': 1, 'b': 2},
            {'a': 2, 'b': 1},
            [],
            [neg])

    def assert_compare(self, expected, row_a, row_b, indicies, directions):
        comparator = RowComparator(indicies, directions)
        result = comparator.cmp(row_a, row_b)
        direction_names = [f.__name__ for f in directions]
        message = (
            "\nExpected %r\n     got %r\na %r\nb %r\nindicies %r\n" +
            "directions %r\n") % (
            expected, result, row_a, row_b, indicies, direction_names)

        self.assertEqual(expected, result, message)

    def test_parse_comparator(self):
        """Build row comparators from specs."""
        idn = identity
        self.assert_row_comparator(['a', 'b'], [idn, idn], ['a', 'b'])
        self.assert_row_comparator(['a', 'b'], [idn, neg], ['a', '-b'])
        self.assert_row_comparator(['b', 'a'], [neg, idn], ['-b', 'a'])

    def assert_row_comparator(
            self, expected_indicies, expected_directions,
            order_spec):
        result = parse_comparator(order_spec)
        message = (
            "\n" +
            "Spec                %r\n" +
            "Expected fields     %r\n" +
            "            got     %r\n" +
            "Expected directions %r\n" +
            "                got %r\n") % (
            order_spec, expected_indicies,
            result.fields, expected_directions, result.directions)
        self.assertEqual(
            (expected_directions, expected_indicies),
            (result.directions, result.fields),
            message)

    def test_sort(self):
        """Sort a stream in different ways."""
        stream = from_iter(
            ['a', 'b', 'c'],
            [
                {'a': 1, 'b': 2, 'c': 3},
                {'a': 3, 'b': 2, 'c': 1},
                {'a': 2, 'b': 2, 'c': 2},
            ])
        sorted_stream = sort_stream(['a', 'b'], stream)
        self.assertEqual([
            {'a': 1, 'b': 2, 'c': 3},
            {'a': 2, 'b': 2, 'c': 2},
            {'a': 3, 'b': 2, 'c': 1},
            ], list(sorted_stream))
        sorted_stream = sort_stream(['b'], stream)
        self.assertEqual([
            {'a': 1, 'b': 2, 'c': 3},
            {'a': 3, 'b': 2, 'c': 1},
            {'a': 2, 'b': 2, 'c': 2},
            ], list(sorted_stream))
        sorted_stream = sort_stream(['b', 'c'], stream)
        self.assertEqual([
            {'a': 3, 'b': 2, 'c': 1},
            {'a': 2, 'b': 2, 'c': 2},
            {'a': 1, 'b': 2, 'c': 3},
            ], list(sorted_stream))
