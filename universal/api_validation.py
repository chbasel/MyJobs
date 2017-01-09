import json
from copy import deepcopy

from django.http import HttpResponse


class ApiValidator(object):
    """
    Record request errors for communication to a client in a standard form.

    Intended for use in Django views. Construct this object, record errors
    found, then return the error response if there are errors.

    Example:
        def some_api_view(request):
            validator = ApiValidator()
            # take apart request
            name = request.POST.get('name', '')
            if not name:
                # record validation errors as we find them
                validator.note_field_error("name", "Report name must not be empty.")
            ... more validation

            if validator.has_errors():
                # if we found any errors, bail with this error response.
                return validator.build_error_response()

            ... do stuff

    """

    def __init__(self):
        self.errors = []

    def note_error(self, error_text):
        """
        Note an error that is not specific to a particular field.

        """
        self.errors.append({'message': error_text})

    def note_field_error(self, field, error_text):
        """
        Note an error which is specific to a particular field.

        """
        self.errors.append({'field': field, 'message': error_text})

    def count_errors(self):
        """
        How many errors have been reported so far?

        :return: number of errors

        """

        return len(self.errors)

    def has_errors(self):
        """
        Have any errors been recorded so far?

        :return: true/false if errors exist

        """
        return bool(self.errors)

    def build_error_response(self):
        """
        Send an error response to a client.

        Example:
        400 bad request
        ...

        [
            {
                'field': 'name',
                'message': 'Report name cannot be empty.',
            },
            {
                'message': 'Order must be under $300.',
            },
        ]

        """
        resp = HttpResponse(content_type='application/json',
                            content=json.dumps(self.errors))
        resp.status_code = 400
        resp.reason_phrase = 'bad request'
        return resp

    def build_document(self):
        """
        Build just the data structures for the error response.

        """
        return list(self.errors)


class FormsApiValidator(object):
    """
    Record request errors for communication to a client in a standard form.

    Intended for use in Django views. Construct this object, record errors
    found, then return the error response if there are errors.

    Example:
        def some_api_view(request):
            validator = FormsApiValidator({
                'forms': {
                    'partner': {
                        'name': {'value': 'Outreach Co.'},
                        'address': {'value': '...'},
                    },
                    'contacts': [
                        {
                            'name': {'value': 'Alice'},
                        },
                        {
                            'name': {'value': 'Bob'},
                        },
                    ],
                },
            })

            # note top level errors
            validator.note_api_error('Something is wrong...')

            # take apart request and note errors
            partner_validator = validator.isolate_validator('partner')
            partner_validator.note_field_error('name', 'Do not punctuate')

            # deeper paths
            partner_validator = validator.isolate_validator('contact', 0)
            partner_validator.note_field_error('name', 'Letter A forbidden.')


            if validator.has_errors():
                # if we found any errors, bail with this error response.
                return validator.build_error_response()

            Error response will be a copy of the input document annotated
            with errors. e.g.:
            {
                'api_errors': ['Something is wrong...'],
                'forms': {
                    'partner': {
                        'name': {
                            'value': 'Outreach Co.',
                            'errors': ['Do not punctuate'],
                        },
                        'address': {'value': '...'},
                    },
                    'contacts': [
                        {
                            'name': {
                                'value': 'Alice',
                                'errors': ['Letter A forbidden'],
                            },
                        },
                        {
                            'name': {'value': 'Bob'},
                        },
                    ],
                },
            }
    """
    def __init__(self, input_doc):
        self.input_doc = input_doc
        self.output_doc = deepcopy(input_doc)
        if 'api_errors' not in self.output_doc:
            self.output_doc['api_errors'] = []
        self.has_form_errors = False

    def forms(self):
        """
        Set of names of forms in the request.
        """
        return set(self.output_doc['forms'].keys())

    def note_has_form_errors(self):
        self.has_form_errors = True

    def has_errors(self):
        """
        Have we found any errors?
        """
        return self.has_form_errors or bool(self.output_doc['api_errors'])

    def note_api_error(self, error):
        """
        Note a top level api error.
        """
        self.output_doc['api_errors'].append(error)

    def build_document(self):
        """
        Build just the data structures for the error response.

        """
        return self.output_doc

    def descend(self, form_path):
        isolated = self.output_doc['forms']
        for segment in form_path:
            isolated = isolated[segment]
        return isolated

    def isolate_validator(self, *form_path):
        """
        Get an isolated validator for the form found at the given path.
        Path can be arbitrarily deep and contain strings for dict keys and
        ints for list indicies.
        """
        isolated = self.descend(form_path)
        return IsolatedFormValidator(isolated, self)

    def iter_validators(self, *form_path):
        """
        For cases where we have lists of similar forms under a key,
        iterate through each one, yielding an isolated validator for each
        one.
        """
        iterable = self.descend(form_path)
        for isolated in iterable:
            yield IsolatedFormValidator(isolated, self)

    def build_error_response(self):
        """
        Send an error response to a client.

        For an example see class docstring.
        """
        resp = HttpResponse(content_type='application/json',
                            content=json.dumps(self.output_doc))
        resp.status_code = 400
        resp.reason_phrase = 'bad request'
        return resp


def collapse_values(data):
    """
    Convert deep hiearchies of objects like: {
        'name': {'value': 'Alice',
    }

    to:

    {'name': 'Alice'}
    """
    result = {}
    for (k, v) in data.iteritems():
        if isinstance(v, dict) and 'value' in v:
            # We are looking at a value dictionary.
            result[k] = v['value']
        elif isinstance(v, dict) and 'errors' in v:
            # We are looking at a dictionary with only errors in it.
            pass
        elif isinstance(v, list):
            # We are looking at a list of collapsible items.
            result[k] = [collapse_values(inner) for inner in v]
        elif isinstance(v, dict):
            # Keep descending. This is an embedded dict of value dicts.
            result[k] = collapse_values(v)
        else:
            raise ValueError(
                'Expected key %s to be a valid root of form data. got %r'
                % (k, v))
    return result


class IsolatedFormValidator(object):
    """Validator pertaining to just a portion of a FormsApiValidator"""
    def __init__(self, form_root, parent):
        self.form_root = form_root
        self.parent = parent

    def get_values(self):
        """
        Get data with values stripped of {'value': ...} wrappers.

        see collapse_values
        """
        return collapse_values(self.form_root)

    def note_field_error(self, field_name, message):
        """
        Note an error on a field in this validator.
        """
        self.parent.note_has_form_errors()
        field = self.form_root.get(field_name, {})
        if 'errors' not in field:
            field['errors'] = []
        field['errors'].append(message)
        self.form_root[field_name] = field

    def get_subvalidator(self, key):
        """Get a validator for a subform within this one"""
        return IsolatedFormValidator(self.form_root[key], self.parent)
