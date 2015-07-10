import imp
import os
import sys

from selenium import webdriver

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.core.urlresolvers import reverse
from django.utils import unittest
from django.utils.unittest.case import TestCase, skipUnless
from selenium.common.exceptions import NoSuchElementException

from myjobs.models import User
from postajob.models import SitePackage
from seo.models import Company, CompanyUser, SeoSite
from seo.tests import patch_settings


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        suite = unittest.TestLoader().loadTestsFromTestCase(JobPostingTests)
        unittest.TextTestRunner().run(suite)


def make_user(address, admin=False):
    """
    Creates a normal user or superuser using the provided address

    Inputs:
    :address: User's email address
    :admin: Boolean, is this user an admin

    Outputs:
    :user: Generated user
    """
    if admin:
        method = 'create_superuser'
    else:
        method = 'create_user'
    user = getattr(User.objects, method)(email=address, send_email=False)
    password = User.objects.make_random_password()
    if isinstance(user, tuple):
        # User.objects.create_user returns (User, created).
        user = user[0]
    # It is less of a headache to set the password now and toggle
    # password_change than it is to pass password into the user creation call,
    # determine if the password was set or if we short-circuited, and then act
    # on that determination.
    user.set_password(password)
    user.password_change = False
    user.is_active = True
    user.is_verified = True
    user.save()
    user.raw_password = password
    return user


# Django's tests work on test databases created specifically for tests.
# Selenium tests work on databases that already exist. While these could be run
# at the same time, it feels more correct to have them remain separate.
@skipUnless('test_posting' in sys.argv, 'Selenium tests are incompatible '
            'with Django tests')
class JobPostingTests(TestCase):
    OVERRIDES = {}
    CREATION_ORDER = []
    test_url = 'localhost'
    test_port = ''

    @classmethod
    def setup_objects(cls):
        """
        This is a big ugly method that sets up objects needed for postajob
        testing.

        Since we're modifying an active database, we need to follow an old
        dumpster diving rule and leave it cleaner than we found it. As such,
        every addition is being added to a list so that they can be reversed.
        This is a little verbose - these additions are being appended to the
        list immediately so that we can adequately revert if something fails.
        """
        #Users:
        # These are all superusers at the moment as the admin page is being
        # used to log in. It isn't guaranteed that a given microsite has a
        # login page set up.

        # admin: Main user for testing
        cls.admin = make_user(address='paj_admin@my.jobs', admin=True)
        cls.CREATION_ORDER.append(cls.admin)
        # admin_2: Secondary company user for a different company
        cls.admin_2 = make_user(address='paj_admin_2@my.jobs', admin=True)
        cls.CREATION_ORDER.append(cls.admin_2)
        # user: User unaffiliated to any company
        cls.user = make_user(address='paj_user@my.jobs', admin=True)
        cls.CREATION_ORDER.append(cls.user)

        # Companies:
        cls.admin_company = Company.objects.create(
            name='Postajob Selenium Company',
            company_slug='postajob-selenium-company',
            member=True, product_access=True, posting_access=True)
        cls.CREATION_ORDER.append(cls.admin_company)
        cls.admin_company_2 = Company.objects.create(
            name='Postajob Selenium Company 2',
            company_slug='postajob-selenium-company-2',
            member=True, product_access=True, posting_access=True)
        cls.CREATION_ORDER.append(cls.admin_company_2)

        # Company Users:
        cls.admin_company_user = CompanyUser.objects.create(
            company=cls.admin_company, user=cls.admin)
        cls.CREATION_ORDER.append(cls.admin_company_user)
        cls.admin_company_user_2 = CompanyUser.objects.create(
            company=cls.admin_company_2, user=cls.admin_2)
        cls.CREATION_ORDER.append(cls.admin_company_user_2)

        # Seo Sites:
        cls.seo_site = SeoSite.objects.create(
            domain='selenium.jobs', name='Selenium Jobs',
            canonical_company=cls.admin_company)
        cls.CREATION_ORDER.append(cls.seo_site)
        cls.seo_site_2 = SeoSite.objects.create(
            domain='selenium2.jobs', name='Selenium Jobs',
            canonical_company=cls.admin_company_2)
        cls.CREATION_ORDER.append(cls.seo_site_2)

        # Site Packages:
        cls.site_package = SitePackage.objects.create(
            owner=cls.admin_company)
        cls.site_package.sites.add(cls.seo_site)
        cls.CREATION_ORDER.append(cls.site_package)
        cls.site_package_2 = SitePackage.objects.create(
            owner=cls.admin_company_2)
        cls.site_package_2.sites.add(cls.seo_site_2)
        cls.CREATION_ORDER.append(cls.site_package_2)

    @classmethod
    def login(cls, user):
        """
        Logs the provided user in using our web driver.

        Inputs:
        :user: User being logged in
        """
        cls.get('/admin/')
        cls.browser.find_element_by_id('id_username').send_keys(user.email)
        cls.browser.find_element_by_id('id_password').send_keys(
            user.raw_password)
        cls.browser.find_element_by_xpath('//input[@value="Log in"]').click()

    @classmethod
    def logout(cls):
        """
        Logs out whoever is logged in, if anyone.
        """
        cls.get('/admin/')
        try:
            element = cls.browser.find_element_by_xpath(
                '//div[@id="user-tools"]//a[2]')
        except NoSuchElementException:
            pass
        else:
            element.click()

    @classmethod
    def post(cls, path='/', data=None, domain=None):
        """
        Shortcut to cls.browser.post(...) with additional options.

        Inputs:
        :path: Path being hit
        :data: A dictionary of values to be posted, if any
        :domain: String used for domain overrides
        """
        data = data or {}
        requested_url = 'http://{domain}{port}{path}'.format(
            domain=cls.test_url, port=cls.test_port, path=path)
        if domain:
            requested_url += '?domain=%s' % domain
        cls.browser.post(requested_url, data=data)

    @classmethod
    def get(cls, path='/', domain=None):
        """
        Shortcut to cls.browser.get(...) with additional options.

        Inputs:
        :path: Path being hit
        :domain: String used for domain overrides
        """
        requested_url = 'http://{domain}{port}{path}'.format(
            domain=cls.test_url, port=cls.test_port, path=path)
        if domain:
            requested_url += '?domain=%s' % domain
        cls.browser.get(requested_url)

    @classmethod
    def setUpClass(cls):
        """
        Sets up the test environment, overriding settings and modifying the db.
        """
        environment = os.environ.get('SETTINGS', '').lower()
        if environment == 'qc':
            print 'Running test_posting with QC settings'
            cls.test_url = 'qc.www.my.jobs'
            qc = imp.load_source('settings.myjobs_qc',
                                 'deploy/settings.myjobs_qc.py')
            cls.OVERRIDES = vars(qc)
        elif environment == 'staging':
            print 'Running test_posting with staging settings'
            cls.test_url = 'staging.www.my.jobs'
            staging = imp.load_source('settings.myjobs_staging',
                                      'deploy/settings.myjobs_staging.py')
            cls.OVERRIDES = vars(staging)
        else:
            assert getattr(settings, 'ENVIRONMENT') != 'Production', \
                'Running test_posting with production settings is unsupported'
            print 'Running test_posting with settings.py'
            # Assuming local; I have to pick a port and runserver defaults to
            # 8000, so...
            cls.test_port = ':8000'
        cls.browser = webdriver.PhantomJS()
        super(JobPostingTests, cls).setUpClass()

        with patch_settings(**cls.OVERRIDES):
            cls.setup_objects()

    @classmethod
    def tearDownClass(cls):
        """
        Deletes all objects created during setup.
        """
        cls.browser.quit()
        with patch_settings(**cls.OVERRIDES):
            for obj in cls.CREATION_ORDER[::-1]:
                obj.delete()
        super(JobPostingTests, cls).tearDownClass()

    def test_show_job_admin(self):
        """
        Ensures that the main postajob admin is functional.

        A company user for the site owner should be able to see all options.
        A company user for a third party or a non-company-user should not.
        """
        with patch_settings(**self.OVERRIDES):
            for user, accessible in [(self.admin, True), (self.admin_2, False),
                                     (self.user, False)]:
                self.login(user)
                self.get(reverse('purchasedmicrosite_admin_overview'),
                         domain=self.seo_site.domain)
                for selector, expected in [('product-listing', 'Product Listing'),
                                           ('our-postings', 'Posted Jobs'),
                                           ('posting-admin', 'Partner Microsite')]:
                    try:
                        element = self.browser.find_element_by_id(selector)
                    except NoSuchElementException:
                        # If the user is not a company user for the owner, this
                        # is expected; if not, we should reraise and fail.
                        if accessible:
                            raise
                    else:
                        self.assertEqual(element.text, expected)
                self.logout()
