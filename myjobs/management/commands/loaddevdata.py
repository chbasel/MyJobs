from datetime import datetime
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from myjobs.models import AppAccess, Activity, Role, User, update_activities
from seo.models import BusinessUnit, Company, Configuration, SeoSite


class Command(BaseCommand):
    @staticmethod
    def add_base_users():
        """
        Creates a generic admin user, and a couple users for
        PRM/user management/other apps.

        """
        user = User.objects.create(
            pk=1,
            email='dev@apps.directemployers.org',
            is_staff=True,
            is_superuser=True,
            is_verified=True,
            first_name='DirectEmployers',
            last_name='Developer',
            user_guid='dev',
        )
        user.set_password('password')
        user.save()

        User.objects.create(
            pk=2,
            email='lukeskywalker@apps.directemployers.org',
            is_verified=True,
            password=user.password,
            first_name='Luke',
            last_name='Skywalker',
            user_guid='lukeskywalker',
        )

        User.objects.create(
            pk=3,
            email='r2d2@apps.directemployers.org',
            is_verified=True,
            password=user.password,
            first_name='R2',
            last_name='D2',
            user_guid='r2d2',
        )

    def add_base_sites(self):
        """
        Creates a few generic base SeoSite instances:

            Basic clones of www.my.jobs:
                www.my.jobs
                localhost
                127.0.0.1
            A company site:
                directemployers.jobs
            A regional site:
                indianapolis.jobs

        """
        # A default SEO group, so Business Units, Faces and all those things
        # can be easily accessible.
        group = Group.objects.create(name="Default SEO Group")

        # Clone of www.my.jobs.
        defaults = {
            'domain': 'www.my.jobs',
            'group': group,
            'site_title': 'Dev My.jobs',
            'site_heading': 'Dev My.jobs',
            'site_description': 'The Right Place for Developers.',
        }
        site = SeoSite.objects.create(pk=1, **defaults)

        config = Configuration.objects.create(
            title='My jobs - development home page',
            status=Configuration.STATUS_PRODUCTION,
            browse_moc_show=True,
            home_page_template='home_page/home_page_listing.html',
        )
        site.configurations.add(config)

        defaults['domain'] = 'localhost'
        site = SeoSite.objects.create(**defaults)
        site.configurations.add(config)

        defaults['domain'] = '127.0.0.1'
        site = SeoSite.objects.create(**defaults)
        site.configurations.add(config)

        # A fake company site.
        bu = BusinessUnit.objects.create(
            id=1,
            date_crawled=datetime.now(),
            date_updated=datetime.now(),
        )
        site = SeoSite.objects.create(
            domain='directemployers.jobs',
            group=group,
            site_title='Dev Jobs for Direct Employers',
            site_heading='Dev Jobs for Direct Employers',
            site_description='The Right Place for Development Jobs.',
        )
        site.business_units.add(bu)

        config = Configuration.objects.create(
            title='Direct Employers Jobs - development home page',
            status=Configuration.STATUS_PRODUCTION,
            browse_moc_show=True,
            home_page_template='home_page/home_page_billboard.html',
        )
        site.configurations.add(config)

        company = Company.objects.create(
            name='DirectEmployers',
            company_slug='directemployers',
            member=True,
            digital_strategies_customer=True,
        )
        company.job_source_ids.add(bu)
        self.add_roles(company)

        # A fake regional site.
        site = SeoSite.objects.create(
            domain='indianapolis.jobs',
            group=group,
            site_title='Dev My.jobs',
            site_heading='Dev My.jobs',
            site_description='The Right Place for Developers in Indiana.',
        )

        config = Configuration.objects.create(
            title='My jobs - development home page',
            status=Configuration.STATUS_PRODUCTION,
            browse_moc_show=True,
            home_page_template='home_page/home_page_listing.html',
        )
        site.configurations.add(config)

    @staticmethod
    def add_roles(company):
        """
        Creates the default activities and roles.
        Adds any user with is_superuser=True to the 'Admin'
        role.

        :param company: The company the role should be created for.

        """
        update_activities()

        company.app_access.add(*AppAccess.objects.all())

        superusers = User.objects.filter(is_superuser=True)

        role, _ = Role.objects.get_or_create(name='Admin', company=company)
        role.activities.add(*Activity.objects.all())
        role.user_set.add(*superusers)

        not_superusers = User.objects.exclude(is_superuser=True)
        role = Role.objects.create(name='Deactivated', company=company)
        role.user_set.add(*not_superusers)

    def handle(self, *args, **options):
        """
        Create default development data to make running the app without
        access to real data easier.

        """
        self.add_base_users()
        self.add_base_sites()
