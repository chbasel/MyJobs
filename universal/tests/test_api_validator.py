from unittest import TestCase

from universal.api_validation import ApiValidator, FormsApiValidator


class TestApiValidator(TestCase):
    def test_note_error(self):
        '''We know when we have errors and can build error documents.'''
        validator = ApiValidator()
        self.assertEqual(False, validator.has_errors())

        validator.note_error("aaa")
        self.assertEqual(True, validator.has_errors())
        self.assertEqual([
            {
                "message": "aaa",
            }], validator.build_document())

        validator.note_error("bbb")
        self.assertEqual(True, validator.has_errors())
        self.assertEqual([
            {
                "message": "aaa",
            },
            {
                "message": "bbb",
            }], validator.build_document())

    def test_note_field_error(self):
        '''We can build error documents with field specific errors.'''
        validator = ApiValidator()
        validator.note_field_error("name", "aaa")
        self.assertEqual(True, validator.has_errors())
        self.assertEqual([
            {
                "field": "name",
                "message": "aaa",
            }], validator.build_document())


class TestFormsApiValidator(TestCase):
    def test_api_errors(self):
        '''
        We know when we have api errors and can build error documents with them
        '''
        validator = FormsApiValidator({})
        self.assertEqual(False, validator.has_errors())

        validator.note_api_error("some error")
        self.assertEqual(True, validator.has_errors())

        self.assertEqual({
            'api_errors': ["some error"],
        }, validator.build_document())

    def test_get_form_data(self):
        '''
        We can isolate a particular form and work on it.
        '''
        validator = FormsApiValidator({
            'forms': {
                'partner': {
                    'name': {'value': 'someone'},
                    'zip': {'value': '90000'},
                },
            },
        })
        self.assertEqual(False, validator.has_errors())
        partner_validator = validator.isolate_validator('partner')

        self.assertEqual({
            'name': 'someone',
            'zip': '90000',
        }, partner_validator.get_values())

        partner_validator.note_field_error('name', 'not capitalized')

        self.assertEqual(True, validator.has_errors())
        self.assertEqual({
            'api_errors': [],
            'forms': {
                'partner': {
                    'name': {
                        'value': 'someone',
                        'errors': ['not capitalized'],
                    },
                    'zip': {'value': '90000'},
                },
            },
        }, validator.build_document())

    def test_get_values_deep(self):
        '''
        We can handle some nesting of data in get_values
        '''
        validator = FormsApiValidator({
            'forms': {
                'partner': {
                    'name': {'value': 'someone'},
                    'zip': {'value': '90000'},
                    'location': {
                        'city': {'value': 'somewhere'},
                        'state': {'errors': ['not here']},
                    },
                },
                'contacts': [
                    {'name': {'value': 'alice'}},
                    {'name': {'value': 'bob'}},
                ]
            },
        })
        partner_validator = validator.isolate_validator('partner')
        self.assertEqual({
            'name': 'someone',
            'zip': '90000',
            'location': {
                'city': 'somewhere',
            },
        }, partner_validator.get_values())

        alice_validator = validator.isolate_validator('contacts', 0)
        self.assertEqual({'name': 'alice'}, alice_validator.get_values())

        bob_validator = validator.isolate_validator('contacts', 1)
        self.assertEqual({'name': 'bob'}, bob_validator.get_values())

    def test_list_of_links(self):
        '''
        We can handle nested lists of linked objects in get_values
        '''
        validator = FormsApiValidator({
            'forms': {
                'partner': {
                    'name': {'value': 'someone'},
                    'tags': [
                        {'pk': {'value': 1}},
                        {'pk': {'value': 2}},
                    ],
                },
            },
        })
        partner_validator = validator.isolate_validator('partner')
        self.assertEqual({
            'name': 'someone',
            'tags': [{'pk': 1}, {'pk': 2}],
        }, partner_validator.get_values())

    def test_note_missing_field(self):
        '''
        We can isolate a particular form and work on it.
        '''
        validator = FormsApiValidator({
            'forms': {
                'partner': {
                    'zip': {'value': '90000'},
                    'location': {
                        'state': {'value': 'NO'},
                    },
                },
            },
        })
        self.assertEqual(False, validator.has_errors())
        partner_validator = validator.isolate_validator('partner')

        partner_validator.note_field_error('zip', 'must be odd')
        location_validator = partner_validator.get_subvalidator('location')
        location_validator.note_field_error('city', 'missing field city')
        location_validator.note_field_error('state', 'not there')

        self.assertEqual(True, validator.has_errors())
        self.assertEqual({
            'api_errors': [],
            'forms': {
                'partner': {
                    'zip': {
                        'value': '90000',
                        'errors': ['must be odd'],
                        },
                    'location': {
                        'state': {
                            'value': 'NO',
                            'errors': ['not there'],
                        },
                        'city': {'errors': ['missing field city']},
                    },
                },
            },
        }, validator.build_document())
