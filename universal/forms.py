from django.forms import ModelForm

from universal.helpers import get_company


class RequestForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.company = get_company(self.request)
        super(RequestForm, self).__init__(*args, **kwargs)


class NormalizedModelForm(ModelForm):
    """
    Extends ModelForm by automatically normalizing string fields on form
    submission. For instance, a field that is entered as "   Foo    Bar" will
    be translated to "Foo Bar".
    """

    def clean(self):
        super(NormalizedModelForm, self).clean()
        self.cleaned_data = {
            key: '\n'.join(' '.join(line.split())
                           for line in value.splitlines())
            if isinstance(value, basestring)
            else value
            for key, value in self.cleaned_data.items()
        }
        return self.cleaned_data
