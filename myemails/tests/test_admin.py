from myjobs.tests.setup import MyJobsBase
from myjobs.forms import MyJobsAdminAuthenticationForm
class TestAdminLoginForm(MyJobsBase):
    
    def test_admin_login_form_has_autocomplete_off(self):
        form = MyJobsAdminAuthenticationForm()
        attributes = form.fields['password'].widget.attrs
        self.assertDictContainsSubset({'autocomplete': 'off'}, attributes,  
            "The widget of the password field of the admin login form should "\
            "have the attribute autocomplete set to 'off'.  Its value \n%s\n"\
            "does not contain {'autocomplete':'off'}" % attributes)
