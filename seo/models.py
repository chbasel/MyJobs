import operator
from DNS import DNSError
from boto.route53.exception import DNSServerError
import newrelic.agent
from slugify import slugify
import Queue

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.contenttypes import generic
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.contrib import messages
from django.core.cache import cache
from django.core import mail
from django.core.validators import MaxValueValidator, ValidationError
from django.db import models
from django.db.models.signals import (post_delete, pre_delete, post_save,
                                      pre_save)
from django.db.models.fields.related import ForeignKey
from django.dispatch import Signal, receiver
from django.template import loader
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from haystack.inputs import Raw
from haystack.query import SQ

from saved_search.models import BaseSavedSearch, SOLR_ESCAPE_CHARS
from taggit.managers import TaggableManager

from moc_coding import models as moc_models
from registration.models import Invitation
from social_links import models as social_models
from seo.route53 import can_send_email, make_mx_record
from seo.search_backend import DESearchQuerySet
from myjobs.models import User, Activity
from mypartners.models import Tag
from universal.accessibility import DOCTYPE_CHOICES, LANGUAGE_CODES_CHOICES
from universal.helpers import (get_domain, get_object_or_none,
                               invitation_context)

import decimal

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^seo\.models\.NonChainedForeignKey"])
add_introspection_rules([], ["^seo\.models\.CommaSeparatedTextField"])


class JobsByBuidManager(models.Manager):
    def get_query_set(self):
        queryset = super(JobsByBuidManager, self).get_query_set()
        if settings.SITE_BUIDS:
            return queryset.filter(buid__in=settings.SITE_BUIDS)
        else:
            return queryset


class ConfigBySiteManager(models.Manager):
    def get_query_set(self):
        return super(ConfigBySiteManager, self).get_query_set().filter(
            seosite__id=settings.SITE_ID)


class GoogleAnalyticsBySiteManager(models.Manager):
    def get_query_set(self):
        return super(GoogleAnalyticsBySiteManager, self).get_query_set().filter(
            seosite__id=settings.SITE_ID)


class NonChainedForeignKey(ForeignKey):
    """
        This field is a special foreign key field designed for same-class FK
        that does not allow...
        - Self-referencing FK (FK to itself)
        - Grandchild relationships (parent has a parent or child has a child)
    """
    def clean(self, value, model_instance):
        super(NonChainedForeignKey, self).clean(value, model_instance)

        if value:
            object_class = model_instance.__class__
            potential_parent = object_class.objects.get(pk=value)
            children = object_class.objects.filter(
                **{self.name:model_instance})

            if value == model_instance.pk:
                raise ValidationError('%s cannot be at parent entity of '
                                      'itself' % model_instance)
            elif children.exists():
                error_list = ", ".join(str(child) for child in children)
                raise ValidationError('%s is a parent of the following '
                                      'entities so cannot be a child itself: '
                                      '%s' % (model_instance, error_list))
            elif getattr(potential_parent, self.name):
                raise ValidationError('%s is a child entity and cannot be a '
                                      'parent' % potential_parent)
        return value


class CustomFacetManager(models.Manager):
    def __getattr__(self, attr, *args):
        if attr.startswith("__"):
            raise AttributeError
        return getattr(self.get_query_set(), attr, *args)


class CustomFacet(BaseSavedSearch):
    """
    Stores search parameters as attributes and builds DESearchQuerySets

    Each CustomFacet object has a foreign key to an SeoSite object. This
    means that in order to create the same saved search across many SEO
    sites, the user will have to copy the saved search once for each site.

    This is made a bit easier by setting save_as == True in the ModelAdmin
    for this model. This allows the user to change the SEO site from the
    FK drop-down, then click "Save as New" to create a new Saved Search
    instance.

    """
    group = models.ForeignKey(Group, blank=True, null=True)
    business_units = models.ManyToManyField('BusinessUnit', blank=True,
                                            null=True)
    country = models.CharField(max_length=800, null=True, blank=True)
    state = models.CharField(max_length=800, null=True, blank=True)
    city = models.CharField(max_length=800, null=True, blank=True)
    keyword = TaggableManager()
    company = models.CharField(max_length=800, null=True, blank=True)
    onet = models.CharField(max_length=10, null=True, blank=True)
    always_show = models.BooleanField("Show With or Without Results",
                                      default=False)

    # Final querystring to send to solr. Updates when object is saved.
    saved_querystring = models.CharField(max_length=10000, blank=True)

    objects = CustomFacetManager()

    field_to_solr_terms = {'title': 'title',
                           'business_units__id': 'buid',
                           'country': 'country',
                           'state': 'state',
                           'onet': 'onet',
                           'keyword__name': 'text',
                           'city': 'location_exact'}

    def __unicode__(self):
        return '%s' % self.name

    def active_site_facet(self):
        facets = self.seositefacet_set.filter(seosite__id=settings.SITE_ID)
        return facets.first()

    def get_op(self):
        """
        Returns boolean operation from active site facet.

        The boolean_operation is currently set in middleware. If it's not set,
        then it's possible that the wrong operation will be returned if there
        are multiple site facets for the active site and they have different
        operations.

        """
        return getattr(self, 'boolean_operation',
                       self.active_site_facet().boolean_operation)

    def clean(self):
        if not self.pk:
            self.save()
        self.name_slug = slugify(self.name)
        self.url_slab = '%s/new-jobs::%s' % (self.name_slug, self.name)
        self.save()

    def save(self, *args, **kwargs):
        if self.querystring:
            sqs = DESearchQuerySet().using('default')
            fail_status = sqs.query.backend.silently_fail
            sqs.query.backend.silently_fail = False

            try:
                sqs.narrow(self.querystring).query.get_results()
            except:
                sqs.query.backend.silently_fail = fail_status
                raise ValidationError("Invalid raw lucene query")

            sqs.query.backend.silently_fail = fail_status

        if not self.pk:
            super(CustomFacet, self).save(*args, **kwargs)

        sqs = DESearchQuerySet().filter(self.create_sq())
        self.saved_querystring = sqs.query.build_query()
        super(CustomFacet, self).save()

    def _attr_dict(self):
        # Any new additions to the custom field that will be searched on must
        # be added to the return value of this method.

        sep = settings.FACET_RULE_DELIMITER
        kw = self.keyword.all()
        cities = [i for i in self.city.split(sep)]

        try:
            onets = self.onet.split(',')
        except AttributeError:
            onets = []
        return {'title': [i for i in self.title.split(sep)],
                'buid': self.business_units.all().values_list('id', flat=True),
                'country': [i for i in self.country.split(sep)],
                'state': [i for i in self.state.split(sep)],
                'onet': onets,
                'text': kw.values_list('name', flat=True) or u'',
                'location_exact': cities}

    def create_sq(self):
        results = []
        for attr, val in self._attr_dict().items():
            if any(val):
                # Build an SQ that joins non empty items in val with boolean or
                filt = reduce(operator.or_,
                              [SQ((u"%s__exact" % attr, i)) for i in val if i])
                results.append(filt)
        if self.querystring:
            results.append(SQ(content=Raw(self.querystring)))

        if results:
            # Build a SQ that joins each non empty SQ in results with boolean and
            retval = reduce(operator.and_, filter(lambda x: x, results))
        else:
            retval = SQ()
        return retval

    def get_sqs(self):
        """
        Returns the DESearchQuerySet object generated by self._attrd_ictionary
        when passed to the Solr backend.

        Warning, do not use for a set of custom facets, it will create a
        database hit for each object. Use .create_sq() directly on the queryset
        instead. We're keeping this method for admin use only.

        """
        attr_dict = self._attr_dict()
        bu = [s.business_units.all() for s in self.sites.all()]
        filts = []
        if bu:
            bu = ','.join(set([str(b.id) for b in reduce(lambda x, y: x | y, bu)]))

        sqs = DESearchQuerySet().models(jobListing).narrow(self._make_qs('buid', bu))

        for attr, val in attr_dict.items():
            if any(val):
                filt = reduce(operator.or_,
                              [SQ(("%s__exact" % attr, i)) for i in val if i])
                filts.append(filt)

        if filts:
            q_filter = reduce(operator.and_, filts)
            sqs = sqs.filter(q_filter)

        return sqs

    def _escape(self, param):
        for c in SOLR_ESCAPE_CHARS:
            param = param.replace(c, '')
        param = param.replace(':', '\\:')
        return param

    def _make_qs(self, field, params):
        """
        Generates the query string which will be passed to Solr directly.

        """
        # If no parameter was passed in, immediately dump back out.
        if not params:
            return ''

        params = params.split(',')
        qs = []
        joinstring = ' OR '

        for thing in params:
            qs.append('%s:%s' % (field, self._escape(thing)))

        return joinstring.join(qs)


@receiver(post_save, sender=CustomFacet)
@receiver(pre_delete, sender=CustomFacet)
def clear_page_cache(sender, **kwargs):
    """
    Clear cache for given domains after CustomFacet object is changed
    in some way.

    """
    # Can't put this in models.py since importing CustomFacet creates a
    # circular import condition.
    obj = kwargs['instance']

    if not obj.seosite_set.exists():
        return

    configs = Configuration.objects.filter(seosite__facets=obj).distinct()

    for config in configs:
        config.save()


class jobListing (models.Model):
    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = 'Job Listing'
        verbose_name_plural = 'Job Listings'

    city = models.CharField(max_length=200, blank=True, null=True)
    citySlug = models.SlugField(blank=True, null=True)
    country = models.CharField(max_length=200, blank=True, null=True)
    countrySlug = models.SlugField(blank=True, null=True)
    country_short = models.CharField(max_length=3, blank=True, null=True,
                                     db_index=True)
    date_new = models.DateTimeField('date new')
    date_updated = models.DateTimeField('date updated')
    description = models.TextField()
    hitkey = models.CharField(max_length=50)
    link = models.URLField(max_length=200)
    location = models.CharField(max_length=200, blank=True, null=True)
    reqid = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=200, blank=True, null=True)
    stateSlug = models.SlugField(blank=True, null=True)
    state_short = models.CharField(max_length=3, blank=True, null=True)
    title = models.CharField(max_length=200)
    titleSlug = models.SlugField(max_length=200, blank=True, null=True,
                                 db_index=True)
    uid = models.IntegerField(db_index=True, unique=True)
    zipcode = models.CharField(max_length=15, null=True, blank=True)

    objects = models.Manager()
    this_site = JobsByBuidManager()

    def save(self):
        self.titleSlug = slugify(self.title)
        self.countrySlug = slugify(self.country)
        self.stateSlug = slugify(self.state)
        self.citySlug = slugify(self.city)

        if self.city and self.state_short:
            self.location = self.city + ', ' + self.state_short
        elif self.city and self.country_short:
            self.location = self.city + ', ' + self.country_short
        elif self.state and self.country_short:
            self.location = self.state + ', ' + self.country_short
        elif self.country:
            self.location = 'Virtual, ' + self.country_short
        else:
            self.location = 'Global'

        super(jobListing, self).save()


class SeoSite(Site):
    class Meta:
        verbose_name = 'Seo Site'
        verbose_name_plural = 'Seo Sites'

    def associated_companies(self):
        buids = self.business_units.all()
        return Company.objects.filter(job_source_ids__id__in=buids)

    def network_sites(self):
        return SeoSite.objects.filter(site_tags__site_tag='network')

    def network_sites_and_this_site(self):
        query = models.Q(site_tags__site_tag='network') | models.Q(id=self.id)
        return SeoSite.objects.filter(query)

    def this_site_only(self):
        # This should return self, but I really want to stay consistent and
        # return a QuerySet so that all the functions can be used
        # identically without knowing the value of postajob_filter_type.
        return SeoSite.objects.filter(id=self.id)

    def company_sites(self):
        companies = self.associated_companies()
        company_buids = companies.values_list('job_source_ids', flat=True)

        sites = SeoSite.objects.filter(business_units__id__in=company_buids)
        return sites.exclude(site_tags__site_tag='network')

    def network_and_company_sites(self):
        companies = self.associated_companies()
        company_buids = companies.values_list('job_source_ids', flat=True)

        query = [models.Q(business_units__id__in=company_buids),
                 models.Q(site_tags__site_tag='network')]

        return SeoSite.objects.filter(reduce(operator.or_, query))

    def all_sites(self):
        return SeoSite.objects.all()

    postajob_filter_options_dict = {
        'network sites only': network_sites,
        'network sites and this site': network_sites_and_this_site,
        'this site only': this_site_only,
        'network sites and sites associated '
        'with the company that owns this site': network_and_company_sites,
        'sites associated with the company that owns this site': company_sites,
        'all sites': all_sites,
    }
    postajob_filter_options = tuple([(k, k) for k in
                                     postajob_filter_options_dict.keys()])

    group = models.ForeignKey('auth.Group', null=True)
    facets = models.ManyToManyField('CustomFacet', null=True, blank=True,
                                    through='SeoSiteFacet')
    configurations = models.ManyToManyField('Configuration', blank=True)
    google_analytics = models.ManyToManyField('GoogleAnalytics', null=True,
                                              blank=True)
    business_units = models.ManyToManyField('BusinessUnit', null=True,
                                            blank=True)
    featured_companies = models.ManyToManyField('Company', null=True,
                                                blank=True)
    microsite_carousel = models.ForeignKey('social_links.MicrositeCarousel',
                                           null=True, blank=True,
                                           on_delete=models.SET_NULL)
    billboard_images = models.ManyToManyField('BillboardImage', blank=True,
                                              null=True)
    site_title = models.CharField('Site Title', max_length=200, blank=True,
                                  default='')
    site_heading = models.CharField('Site Heading', max_length=200, blank=True,
                                    default='')
    site_description = models.CharField('Site Description', max_length=200,
                                        blank=True, default='')
    google_analytics_campaigns = models.ForeignKey('GoogleAnalyticsCampaign',
                                                   null=True, blank=True)
    view_sources = models.ForeignKey('ViewSource', null=True, blank=True)
    ats_source_codes = models.ManyToManyField('ATSSourceCode', null=True,
                                              blank=True)
    special_commitments = models.ManyToManyField('SpecialCommitment',
                                                 blank=True, null=True)
    site_tags = models.ManyToManyField('SiteTag', blank=True, null=True)

    # The "designated" site package specific to this seosite.
    # This site should be the only site attached to site_package.
    site_package = models.ForeignKey('postajob.SitePackage', null=True,
                                     blank=True, on_delete=models.SET_NULL)

    postajob_filter_type = models.CharField(max_length=255,
                                            choices=postajob_filter_options,
                                            default='this site only')
    canonical_company = models.ForeignKey('Company', blank=True, null=True,
                                          on_delete=models.SET_NULL,
                                          related_name='canonical_company_for')

    parent_site = NonChainedForeignKey('self', blank=True, null=True,
                                       on_delete=models.SET_NULL,
                                       related_name='child_sites')

    email_domain = models.CharField(max_length=255, default='my.jobs')

    def clean_domain(self):
        """
        Ensures that an MX record exists for a given domain, if possible.
        This allows the domain as an option for email_domain.
        """
        if not hasattr(mail, 'outbox'):
            # Don't try creating MX records when running tests.
            try:
                can_send = can_send_email(self.domain)
                if can_send is not None and not can_send:
                    make_mx_record(self.domain)
            except (DNSError, DNSServerError):
                # This will create some false negatives but there's not much
                # to be done about that aside from multiple retries.
                pass
        return self.domain

    def clean_email_domain(self):
        # TODO: Finish after MX Records are sorted out
        # Determine if the company actually has permission to use the domain.
        domains = self.canonical_company.get_seo_sites().values_list('domain',
                                                                     flat=True)
        domains = [get_domain(domain) for domain in domains]
        domains.append('my.jobs')
        if self.email_domain not in domains:
            raise ValidationError('You can only send emails from a domain '
                                  'that is associated with your company.')

        # Ensure that we have an MX record for the domain.
        if not can_send_email(self.email_domain):
            raise ValidationError('You do not currently have the ability '
                                  'to send emails from this domain.')
        return self.email_domain

    def postajob_site_list(self):
        filter_function = self.postajob_filter_options_dict.get(
            self.postajob_filter_type, SeoSite.this_site_only)
        return filter_function(self)

    @staticmethod
    def clear_caches(sites):
        # Increment Configuration revision attributes, which is used
        # when calculating a custom_cache_pages cache key prefix.
        # This will effectively expire the page cache for custom_cache_page
        # views_
        configs = Configuration.objects.filter(seosite__in=sites)
        # https://docs.djangoproject.com
        # /en/dev/topics/db/queries/#query-expressions
        configs.update(revision=models.F('revision') + 1)
        Configuration.clear_caches(configs)
        # Delete domain-based cache entries that don't use the
        # custom_cache_page prefix
        site_cache_keys = ['%s:SeoSite' % site.domain for site in sites]
        buid_cache_keys = ['%s:buids' % key for key in site_cache_keys]
        social_cache_keys = ['%s:social_links' % site.domain for site in sites]
        cache.delete_many(site_cache_keys + buid_cache_keys + social_cache_keys)

    def email_domain_choices(self,):
        from postajob.models import CompanyProfile
        profile = get_object_or_none(CompanyProfile,
                                     company=self.canonical_company)
        email_domain_field = SeoSite._meta.get_field('email_domain')
        choices = [
            (email_domain_field.get_default(), email_domain_field.get_default()),
            (self.domain, self.domain),
        ]
        if profile and profile.outgoing_email_domain:
            choices.append((profile.outgoing_email_domain,
                            profile.outgoing_email_domain))
        return choices

    def save(self, *args, **kwargs):
        # always call clean if the parent_site entry exists to prevent invalid
        # relationships
        if self.parent_site: self.clean_fields()
        super(SeoSite, self).save(*args, **kwargs)
        self.clear_caches([self])

    def user_has_access(self, user):
        """
        In order for a user to have access they must be assigned a role in the
        Company that owns the SeoSite.

        """
        site_buids = self.business_units.all()
        companies = Company.objects.filter(job_source_ids__in=site_buids)

        return companies.filter(role__user=user).exists()

    def get_companies(self):
        site_buids = self.business_units.all()
        return Company.objects.filter(job_source_ids__in=site_buids).distinct()


class SeoSiteFacet(models.Model):
    """This model defines the default Custom Facet(s) for a given site."""
    STANDARD = 'STD'
    DEFAULT = 'DFT'
    FEATURED = 'FTD'
    FACET_TYPE_CHOICES = ((STANDARD, 'Standard'), (DEFAULT, 'Default'),
                          (FEATURED, 'Featured'), )

    BOOLEAN_CHOICES = (('or', 'OR'), ('and', 'AND'), )

    FACET_GROUP_CHOICES = ((1, 'Facet Group 1'), (2, 'Facet Group 2'),
                           (3, 'Facet Group 3'), (4, 'Facet Group 4'))

    facet_group = models.IntegerField(choices=FACET_GROUP_CHOICES, default=1)
    seosite = models.ForeignKey('SeoSite', verbose_name="Seo Site")
    customfacet = models.ForeignKey('CustomFacet', verbose_name="Custom Facet")
    facet_type = models.CharField(max_length=4,
                                  choices=FACET_TYPE_CHOICES,
                                  default=STANDARD,
                                  verbose_name="Facet Type",
                                  db_index=True)
    boolean_operation = models.CharField(max_length=3,
                                         default='or',
                                         choices=BOOLEAN_CHOICES,
                                         verbose_name="Boolean Operation",
                                         db_index=True)
    boolean_choices = ['or', 'and']

    class Meta:
        verbose_name = "Seo Site Facet"
        verbose_name_plural = "Seo Site Facets"


class Company(models.Model):
    """
    This model defines companies that come from various job sources (currently
    business units).

    """
    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['name']
        unique_together = ('name', 'user_created')


    def __unicode__(self):
        return self.name

    natural_key = __unicode__


    def save(self, *args, **kwargs):
        exists = str(self.pk).isdigit()

        self.company_slug = slugify(self.name)
        super(Company, self).save(*args, **kwargs)

        if not exists:
            default_tags = [
                {"name": "Veteran", "hex_color": "5EB94E"},
                {"name": "Female", "hex_color": "4BB1CF"},
                {"name": "Minority", "hex_color": "FAA732"},
                {"name": "Disability", "hex_color": "808A9A"},
                {"name": "Disabled Veteran", "hex_color": "659274"}
            ]
            for tag in default_tags:
                Tag.objects.get_or_create(company=self, **tag)

            # create the default admin role
            admin_role = self.role_set.create(name="Admin")
            admin_role.activities = Activity.objects.all()

    def associated_jobs(self):
        b_units = self.job_source_ids.all()
        job_count = 0
        for unit in b_units:
            job_count += unit.associated_jobs
        return job_count

    def featured_on(self):
        return ", ".join(self.seosite_set.all().values_list("domain",
                                                            flat=True))

    @property
    def has_features(self):
        """
        Convenience read-only property which returns whether the company has
        any features enabled.
        """

        return self.app_access.exists()

    @property
    def admins(self):
        """Returns all users associated with this company's "Admin" role."""

        admin_role = self.role_set.get(name='Admin')
        return User.objects.filter(roles=admin_role).distinct()

    name = models.CharField('Name', max_length=200)
    company_slug = models.SlugField('Company Slug', max_length=200, null=True,
                                    blank=True)
    job_source_ids = models.ManyToManyField('BusinessUnit')
    logo_url = models.URLField('Logo URL', max_length=200, null=True,
                               blank=True, help_text="The url for the 100x50 "
                               "logo image for this company.")
    linkedin_id = models.CharField('LinkedIn Company ID',
                                   max_length=20, null=True, blank=True,
                                   help_text="The LinkedIn issued company "
                                   "ID for this company.")
    og_img = models.URLField('Open Graph Image URL', max_length=200, null=True,
                             blank=True, help_text="The url for the large "
                             "format logo for use when sharing jobs on "
                             "LinkedIn, and other social platforms that "
                             "support OpenGraph.")
    canonical_microsite = models.URLField('Canonical Microsite URL',
                                          max_length=200, null=True,
                                          blank=True, help_text="The primary "
                                          "directemployers microsite for this "
                                          "company.")
    member = models.BooleanField('DirectEmployers Association Member',
                                 default=False)
    social_links = generic.GenericRelation(social_models.SocialLink,
                                           object_id_field='id',
                                           content_type_field='content_type')
    digital_strategies_customer = models.BooleanField(
        'Digital Strategies Customer', default=False)
    enhanced = models.BooleanField('Enhanced', default=False)
    site_package = models.ForeignKey('postajob.SitePackage', null=True,
                                     on_delete=models.SET_NULL)

    prm_saved_search_sites = models.ManyToManyField('SeoSite', null=True,
                                                    blank=True)
    password_expiration = models.BooleanField(
        'Enforce Password Expiration', default=False)

    # Permissions
    app_access = models.ManyToManyField(
        'myjobs.AppAccess',
        blank=True, verbose_name="App-Level Access")
    user_created = models.BooleanField(default=False)

    def get_seo_sites(self):
        """
        Retrieves a given company's microsites

        Inputs:
        :company: Company whose microsites are being retrieved

        Outputs:
        :microsites: List of microsites
        """
        buids = self.job_source_ids.all()

        microsites = SeoSite.objects.filter(models.Q(business_units__in=buids)
                                            | models.Q(canonical_company=self))
        return microsites

    @property
    def prm_access(self):
        """
        Read-only property that returns whether or not a company has access
        to PRM features.
        """

        return "PRM" in self.app_access.values_list("name", flat=True)


    def user_has_access(self, user):
        """
        Returns whether or not the given user can be tied back to the company.
        """

        return user.pk in self.role_set.values_list('user', flat=True)

    @property
    def has_packages(self):
        return self.sitepackage_set.filter(
            sites__in=settings.SITE.postajob_site_list()).exists()

    @property
    def enabled_access(self):
        """Returns a list of app access names associated with this company."""

        return filter(bool, self.app_access.values_list('name', flat=True))

    @property
    def activities(self):
        return Activity.objects.select_related('app_access').filter(
            app_access__in=self.app_access.all())


class FeaturedCompany(models.Model):
    """
    Featured company option for a given multi-company SeoSite.
    """
    seosite = models.ForeignKey('SeoSite')
    company = models.ForeignKey('Company')
    is_featured = models.BooleanField('Featured Company?', default=False)


class SpecialCommitment(models.Model):
    """
    Special Commits are used on a site by site basis to place Schema.org
    tags on the site. This flags the site as containing jobs for a distinct
    set of job seekers.
    """
    name = models.CharField(max_length=200)
    commit = models.CharField(
        'Schema.org Commit Code',
        help_text="VeteranCommit, SummerCommit, etc...",
        max_length=200)

    def __unicode__(self):
        return self.name

    def committed_sites(self):
        return ", ".join(self.seosite_set.all().values_list("domain",
                                                            flat=True))

    class Meta:
        verbose_name = "Special Commitment"
        verbose_name_plural = "Special Commitments"


class GoogleAnalyticsCampaign(models.Model):
    """
    Defines a Google Analytics Campaign
    More Info:
    http://support.google.com/googleanalytics/bin/answer.py?hl=en&answer=55578

    If there is ever a need for a non-google analytics model, create a base
    class for this model first.
    """
    name = models.CharField(max_length=200, default='')
    group = models.ForeignKey('auth.group', null=True)
    campaign_source = models.CharField(
        help_text=" (referrer: google, citysearch, newsletter4)",
        max_length=200, default='')
    campaign_medium = models.CharField(
        help_text=" (marketing medium: cpc, banner, email)",
        max_length=200, default='')
    campaign_name = models.CharField(
        help_text="(product, promo code, or slogan)",
        max_length=200, default='')
    campaign_term = models.CharField(
        help_text="(identify the paid keywords)",
        max_length=200, default='')
    campaign_content = models.CharField(
        help_text="(use to differentiate ads)",
        max_length=200, default='')

    def __unicode__(self):
        return "Google Analytics Campaign - %s" % self.campaign_name

    def sites(self):
        return ", ".join(self.seosite_set.all().values_list("domain",
                                                            flat=True))

    class Meta:
        verbose_name = "Google Analytics Campaign"
        verbose_name_plural = "Google Analytics Campaigns"


class URINameValuePair(models.Model):
    """
    Create a name value pair for use on a URL
    """
    name = models.CharField(max_length=200, default='')
    value= models.CharField(max_length=200, default='')
    group = models.ForeignKey('auth.group', null=True)

    def __unicode__(self):
        return "%s=%s" % (self.name, self.value)

    class Meta:
        abstract = True


class ATSSourceCode(URINameValuePair):
    """
    Instance of URINameValuePairmodel for tracking a specific ATS source code
    """
    ats_name = models.CharField(max_length=200,default='')

    def sites(self):
        return ", ".join(self.seosite_set.all().values_list("domain",
                                                            flat=True))

    class Meta:
        verbose_name = 'ATS Source Code'


class ViewSource(models.Model):
    """
    Defines a source code to override the default provided by the job source
    """
    name = models.CharField(max_length=200, default='')
    view_source = models.IntegerField(max_length=20, default='')

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.view_source)

    def sites(self):
        return ", ".join(self.seosite_set.all().values_list("domain",
                                                            flat=True))

    class Meta:
        verbose_name = "View Source"
        verbose_name_plural = "View Sources"


class BillboardImage(models.Model):
    def __unicode__(self):
        return "%s: %s" % (self.title, str(self.id))

    title = models.CharField('Title', max_length=200)
    group = models.ForeignKey('auth.group', null=True)
    image_url = models.URLField('Image URL', max_length=200)
    copyright_info = models.CharField('Copyright Info', max_length=200)
    source_url = models.URLField('Source URL', max_length=200)
    logo_url = models.URLField('Logo Image URL',
                               max_length=200, null=True, blank=True)
    sponsor_url = models.URLField('Logo Sponsor URL',
                                  max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = 'Billboard Image'
        verbose_name_plural = 'Billboard Images'

    def on_sites(self):
        return ", ".join(self.seosite_set.all().values_list("domain",
                                                            flat=True))

    def number_of_hotspots(self):
        return self.billboardhotspot_set.all().count()

    def has_hotspots(self):
        # returns True if the the billboard has hotspots.
        return self.number_of_hotspots() > 0
    has_hotspots.boolean = True


class BillboardHotspot(models.Model):
    billboard_image = models.ForeignKey(BillboardImage)
    title = models.CharField('Title', max_length=50,
                             help_text="Max 50 characters")
    text = models.CharField('Text', max_length=140,
                            help_text="Max 140 characters.  "
                                      "Use HTML markup for line breaks "
                                      "and formatting.")
    url = models.URLField('URL', null=True, blank=True)
    display_url = models.TextField('Display URL', null=True, blank=True)
    offset_x = models.IntegerField('Offset X')
    offset_y = models.IntegerField('Offset Y')
    primary_color = models.CharField('Primary Color', max_length=6,
                                     default='5A6D81')
    font_color = models.CharField('Font Color', max_length=6, default='FFFFFF')
    border_color = models.CharField('Border Color', max_length=6,
                                    default='FFFFFF')

    class Meta:
        verbose_name = 'Billboard Hotspot'


class SiteTag(models.Model):
    """
    Defines a tag to help categorize SeoSites. These tags will allow us to
    arbitrarily group different kinds of sites (members, companies,
    network sites, etc.)
    """
    site_tag = models.CharField('Site Tag', max_length=100, unique=True)
    tag_navigation = models.BooleanField('Tag can be used for navigation',
                                         default=False,
                                         help_text='Tag can be used for '
                                                   'navigation by users. '
                                                   'Viewable by public.')

    def __unicode__(self):
        return "%s" % self.site_tag

    class Meta:
        verbose_name = 'Site Tag'


class SeoSiteRedirect(models.Model):
    redirect_url = models.CharField('domain name', max_length=100,
                                    db_index=True)
    seosite = models.ForeignKey(SeoSite)

    class Meta:
        unique_together = ["redirect_url", "seosite"]
        verbose_name = 'Seo Site Redirect'
        verbose_name_plural = 'Seo Site Redirects'


class Configuration(models.Model):
    ORDER_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
        (9, 9),
    )

    STATUS_STAGING = 1
    STATUS_PRODUCTION = 2
    STATUSES = {
        STATUS_STAGING: 'Staging',
        STATUS_PRODUCTION: 'Production',
    }
    STATUS_CHOICES = STATUSES.items()

    HOME_ICON_NONE = 1
    HOME_ICON_BOTTOM = 2
    HOME_ICON_TOP = 3
    HOME_ICON_CHOICES = (
        (HOME_ICON_NONE, 'None'),
        (HOME_ICON_BOTTOM, 'Bottom'),
        (HOME_ICON_TOP, 'Top')
    )

    TEMPLATE_V1 = 'v1'
    TEMPLATE_V2 = 'v2'
    TEMPLATE_VERSION_CHOICES = (
        (TEMPLATE_V1, 'Version 1'),
        (TEMPLATE_V2, 'Version 2'),
    )

    def __init__(self, *args, **kwargs):
        super(Configuration, self).__init__(*args, **kwargs)
        self._original_browse_moc_show = self.browse_moc_show
        self.browse_mapped_moc_show = self.browse_moc_show
        self.browse_mapped_moc_text = self.browse_moc_text
        self.browse_mapped_moc_order = self.browse_moc_order

    @staticmethod
    def clear_caches(configs):
        # Delete all cached configurations used to determine cache key prefixes
        # in directseo.seo.decorators.custom_cache_page because the
        # configuration revision referenced in the key_prefix has changed.
        sites = SeoSite.objects.filter(configurations__in=configs)
        statuses = set()
        for config in configs:
            statuses.add(config.status)
        for status in statuses:
            cache.delete_many(["%s:config:%s" % (site.domain, status) for
                               site in sites.all()])
            cache.delete_many(["jobs_count::%s" % site.pk for
                               site in  sites.all()])

    def clear_cache(self):
        self.clear_caches([self])

    def save(self, *args, **kwargs):
        # Increment the revision number so a new cache key will be used for urls
        # of the seosites linked to this configuration.
        self.revision += 1
        super(Configuration, self).save(*args, **kwargs)
        self.clear_caches([self])

    def status_title(self):
        return self.STATUSES.get(self.status, 'Pending')

    def __unicode__(self):
        if self.title:
            return "%s -- %s rev.%s" % (self.title, self.status_title(),
                                        str(self.id))
        else:
            return "%s: rev.%s" % (self.status_title(), str(self.id))

    def show_sites(self):
        return ", ".join(self.seosite_set.all().values_list("domain",
                                                            flat=True))

    def get_template(self, template_string):
        """
        Determine if the current configuration is set to use v2 templates,
        and if so, check whether or not the template provided in template_string
        exists in the v2 directory.

        :param template_string: Original path of desired template
        :return: Original path or v2 path if exists and enabled

        """
        template_version = self.TEMPLATE_V1

        if self.template_version not in (self.TEMPLATE_V1, None):
            try:
                version_string = '%s/%s' % (self.template_version, template_string)
                loader.get_template(version_string)
                template_string = version_string
                template_version = self.template_version
            except loader.TemplateDoesNotExist:
                pass

        param = "template_version"
        newrelic.agent.add_custom_parameter(param, template_version)

        return template_string

    title = models.CharField(max_length=50, null=True)
    # version control
    status = models.IntegerField('Status', default=1, choices=STATUS_CHOICES,
                                 null=True, blank=True, db_index=True)
    # navigation section
    defaultBlurb = models.TextField('Blurb Text', blank=True, null=True)
    defaultBlurbTitle = models.CharField('Blurb Title', max_length=100,
                                         blank=True, null=True)
    # default_blurb_always_show = models.BooleanField('Always Show',
    #                                                default=False)
    browse_country_show = models.BooleanField('Show', default=True)
    browse_state_show = models.BooleanField('Show', default=True)
    browse_city_show = models.BooleanField('Show', default=True)
    browse_title_show = models.BooleanField('Show', default=True)
    browse_facet_show = models.BooleanField('Show', default=False)
    browse_facet_show_2 = models.BooleanField('Show', default=False)
    browse_facet_show_3 = models.BooleanField('Show', default=False)
    browse_facet_show_4 = models.BooleanField('Show', default=False)
    browse_moc_show = models.BooleanField('Show', default=False)
    browse_company_show = models.BooleanField('Show', default=False)

    browse_country_text = models.CharField('Heading for Country Facet',
                                           default='Country',
                                           max_length=50)
    browse_state_text = models.CharField('Heading for State Facet',
                                         default='State',
                                         max_length=50)
    browse_city_text = models.CharField('Heading for City Facet',
                                        default='City',
                                        max_length=50)
    browse_title_text = models.CharField('Heading for Title Facet',
                                         default='Title',
                                         max_length=50)
    browse_facet_text = models.CharField('Heading for Custom Facet Group 1',
                                         default='Job Profiles',
                                         max_length=50)
    browse_facet_text_2 = models.CharField('Heading for Custom Facet Group 2',
                                           default='Job Profiles',
                                           max_length=50)
    browse_facet_text_3 = models.CharField('Heading for Custom Facet Group 3',
                                           default='Job Profiles',
                                           max_length=50)
    browse_facet_text_4 = models.CharField('Heading for Custom Facet Group 4',
                                           default='Job Profiles',
                                           max_length=50)
    browse_moc_text = models.CharField('Heading for MOC Facet',
                                       default='Military Titles',
                                       max_length=50)
    browse_company_text = models.CharField('Heading for Company Facet',
                                           default='Company',
                                           max_length=50)

    browse_country_order = models.IntegerField('Order', default=3,
                                               choices=ORDER_CHOICES)
    browse_state_order = models.IntegerField('Order', default=4,
                                             choices=ORDER_CHOICES)
    browse_city_order = models.IntegerField('Order', default=5,
                                            choices=ORDER_CHOICES)
    browse_title_order = models.IntegerField('Order', default=6,
                                             choices=ORDER_CHOICES)
    browse_facet_order = models.IntegerField('Order', default=1,
                                             choices=ORDER_CHOICES)
    browse_facet_order_2 = models.IntegerField('Order', default=2,
                                               choices=ORDER_CHOICES)
    browse_facet_order_3 = models.IntegerField('Order', default=3,
                                               choices=ORDER_CHOICES)
    browse_facet_order_4 = models.IntegerField('Order', default=4,
                                               choices=ORDER_CHOICES)
    browse_moc_order = models.IntegerField('Order', default=1,
                                           choices=ORDER_CHOICES)
    browse_company_order = models.IntegerField('Order', default=7,
                                               choices=ORDER_CHOICES)
    num_subnav_items_to_show = models.IntegerField('Subnav Options Shown',
                                                   default=9)
    num_filter_items_to_show = models.IntegerField('Filter Options Shown',
                                                   default=10)
    num_job_items_to_show = models.IntegerField('Job Listings Shown',
                                                default=15)
    # url options
    location_tag = models.CharField(max_length=50, default='jobs')
    title_tag = models.CharField(max_length=50, default='jobs-in')
    facet_tag = models.CharField(max_length=50, default='new-jobs')
    moc_tag = models.CharField(max_length=50, default='vet-jobs')
    company_tag = models.CharField(max_length=50, default='careers')
    # template section
    doc_type = models.CharField(max_length=255,
                                choices=DOCTYPE_CHOICES,
                                default='<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 '
                                        'Transitional//EN" "http://'
                                        'www.w3.org/TR/html4/loose.dtd">')
    language_code = models.CharField(max_length=16,
                                     choices=LANGUAGE_CODES_CHOICES,
                                     default='en')
    meta = models.TextField(null=True, blank=True)
    wide_header = models.TextField(null=True, blank=True)
    header = models.TextField(null=True, blank=True)
    body = models.TextField('Custom Homepage Body', null=True, blank=True)
    wide_footer = models.TextField(null=True, blank=True)
    footer = models.TextField(null=True, blank=True)
    view_all_jobs_detail = models.BooleanField(
        'Use detailed "View All Jobs" label',
        help_text='Include site title details in "View All Jobs" link text',
        default=False)
    # site links
    directemployers_link = models.URLField(max_length=200,
                                           default='http://directemployers.org')
    show_social_footer = models.BooleanField('Show Social Footer', default=True,
                                             help_text='Include social footer '
                                                       'on job listing pages.')

    # stylesheet manytomany relationship
    backgroundColor = models.CharField(max_length=6, blank=True, null=True)
    fontColor = models.CharField(max_length=6, default='666666')
    primaryColor = models.CharField(max_length=6, default='990000')
    # manage authorization
    group = models.ForeignKey('auth.Group', null=True)
    # revision field for cache key decorator
    revision = models.IntegerField('Revision', default=1)

    # home page template settings
    home_page_template = models.CharField(
        'Home Page Template', max_length=200,
        default='home_page/home_page_listing.html'
    )
    show_home_microsite_carousel = models.BooleanField('Show Microsite Carousel'
                                                       ' on Home Page',
                                                       default=False)
    show_home_social_footer = models.BooleanField('Show Social Footer on'
                                                  ' Home Page',
                                                  default=False)
    publisher = models.CharField('Google plus page id', max_length=50,
                                 blank=True,
                                 help_text="Google plus page id for "
                                           "publisher tag")

    objects = models.Manager()
    this_site = ConfigBySiteManager()

    # Value from 0 to 1 showing what percent of featured jobs to display
    # per page
    percent_featured = models.DecimalField(
        max_digits=3, decimal_places=2,
        default=decimal.Decimal('.5'),
        validators=[MaxValueValidator(decimal.Decimal('1.00'))],
        verbose_name="Featured Jobs Maximum Percentage")

    # widget related items
    show_saved_search_widget = models.BooleanField(default=False,
                                                   help_text='Show saved '
                                                             'search widget '
                                                             'on job listing '
                                                             'page.')
    use_secure_blocks = models.BooleanField(default=False,
                                            help_text='Use secure blocks for '
                                                      'displaying widgets.')

    template_version = models.CharField(max_length=5, default='v1',
                                        choices=TEMPLATE_VERSION_CHOICES)

    moc_label = models.CharField(max_length=255, blank=True)
    what_label = models.CharField(max_length=255, blank=True)
    where_label = models.CharField(max_length=255, blank=True)

    moc_placeholder = models.CharField(max_length=255, blank=True)
    what_placeholder = models.CharField(max_length=255, blank=True)
    where_placeholder = models.CharField(max_length=255, blank=True)

    moc_helptext = models.TextField(blank=True)
    what_helptext = models.TextField(blank=True)
    where_helptext = models.TextField(blank=True)


to_string = lambda param, values: " or ".join("=".join([param, value])
                                              for value in values.split('|')
                                              if value)


class QueryParameter(models.Model):
    value = models.CharField(max_length=200,
                             help_text=_('The part after the equals sign'))

    class Meta:
        abstract = True


@python_2_unicode_compatible
class QParameter(QueryParameter):
    redirect = models.OneToOneField('QueryRedirect', null=True,
                                    on_delete=models.CASCADE,
                                    related_name='q')

    def __str__(self):
        return to_string(param='q', values=self.value)


@python_2_unicode_compatible
class LocationParameter(QueryParameter):
    redirect = models.OneToOneField('QueryRedirect', null=True,
                                    on_delete=models.CASCADE,
                                    related_name='location')

    def __str__(self):
        return to_string(param='location', values=self.value)


@python_2_unicode_compatible
class MocParameter(QueryParameter):
    redirect = models.OneToOneField('QueryRedirect', null=True,
                                    on_delete=models.CASCADE,
                                    related_name='moc')

    def __str__(self):
        return to_string(param='moc', values=self.value)


@python_2_unicode_compatible
class QueryRedirect(models.Model):
    site = models.ForeignKey('sites.Site')
    old_path = models.CharField(_('redirect from'), max_length=200,
                                db_index=True,
                                help_text=_(
                                    "This should be an absolute path, "
                                    "excluding the domain name. Example: "
                                    "'/events/search/'."))
    new_path = models.CharField(_('redirect to'), max_length=200, blank=True,
                                help_text=_(
                                    "This can be either an absolute "
                                    "path (as above) or a full URL starting "
                                    "with 'http://' or 'https://'."))

    def __str__(self):
        return "%s ---> %s" % (self.old_path, self.new_path)


class GoogleAnalytics (models.Model):
    web_property_id = models.CharField('Web Property ID', max_length=20)
    group = models.ForeignKey('auth.Group', null=True)

    objects = models.Manager()
    this_site = GoogleAnalyticsBySiteManager()

    def show_sites(self):
        return ", ".join(self.seosite_set.all().values_list("domain",flat=True))

    class Meta:
        verbose_name = 'Google Analytics'
        verbose_name_plural = 'Google Analytics'

    def __unicode__(self):
        return self.web_property_id


class JobFeed(Feed):
    link = ""

    def __init__(self, type):
        self.type = type

    def item_title(self, item):
        # Creates a location description string from locations fields if
        # they exist
        loc_list = [item[key] for key in
            ['country_short', 'state_short', 'city'] if item.get(key)]
        title_loc = "-".join(loc_list)
        return "(%s) %s" % (title_loc, item['title'])

    def item_description(self, item):
        return item['description']

    def item_link(self, item):
        is_posted = item.get('is_posted', False)
        if is_posted:
            # If an item is posted, instead of using the
            # redirect link we use the http://site.jobs/guid/jobs/ link
            # that goes directly to the microsite.
            return "/%s/job/" % item['guid']

        else:
            vs = settings.FEED_VIEW_SOURCES.get(self.type, 20)
            return '/%s%s' % (item['guid'], vs)

    def item_pubdate(self, item):
        return item['date_new']


class BusinessUnit(models.Model):
    def __unicode__(self):
        return "%s: %s" % (self.title, str(self.id))

    class Meta:
        verbose_name = 'Business Unit'
        verbose_name_plural = 'Business Units'

    def save(self, *args, **kwargs):
        self.title_slug = slugify(self.title)
        super(BusinessUnit, self).save(*args, **kwargs)

    def show_sites(self):
        return ", ".join(self.seosite_set.all().values_list("domain",
                                                            flat=True))

    id = models.IntegerField('Business Unit Id', max_length=10,
                             primary_key=True)
    title = models.CharField(max_length=500, null=True, blank=True)
    title_slug = models.SlugField(max_length=500, null=True, blank=True)
    date_crawled = models.DateTimeField('Date Crawled')
    date_updated = models.DateTimeField('Date Updated')
    associated_jobs = models.IntegerField('Associated Jobs', default=0)
    customcareers = generic.GenericRelation(moc_models.CustomCareer)
    federal_contractor = models.BooleanField(default=False)
    ignore_includeinindex = models.BooleanField('Ignore "Include In Index"',
                                                default=False)

    # True if a BusinessUnit's descriptions are in markdown
    # Assumes that new business units will have support markdown
    enable_markdown = models.BooleanField('Enable Markdown for job '
                                          'descriptions', default=True)
    site_packages = models.ManyToManyField('postajob.SitePackage', null=True,
                                           blank=True)

    @staticmethod
    def clear_cache(buid):
        """Clears the cache for related sites."""
        sites = SeoSite.objects.filter(business_units=buid).exclude(
            site_tags__site_tag='network')
        SeoSite.clear_caches(sites)


class Country(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    abbrev = models.CharField(max_length=255, blank=True, null=True,
                              db_index=True)
    abbrev_short = models.CharField(max_length=255, blank=True, null=True,
                                    db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'


class CustomPage(FlatPage):
    group = models.ForeignKey(Group, blank=True, null=True)
    meta = models.TextField(blank=True)
    meta_description = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Custom Page'
        verbose_name_plural = 'Custom Pages'


class CompanyUser(models.Model):
    GROUP_NAME = 'Employer'
    ADMIN_GROUP_NAME = 'Partner Microsite Admin'

    user = models.ForeignKey(User)
    company = models.ForeignKey(Company)
    date_added = models.DateTimeField(auto_now=True)
    group = models.ManyToManyField('auth.Group', blank=True)

    def __unicode__(self):
        return 'Admin %s for %s' % (self.user.email, self.company.name)

    def save(self, *args, **kwargs):
        """
        Adds the user to the Employer group if it wasn't already a member.

        If the user is already a member of the Employer group, the Group app
        is smart enough to not add it a second time.
        """

        using = kwargs.get('using', 'default')

        inviting_user = kwargs.pop('inviting_user', None)
        group = Group.objects.using(using).get(name=self.GROUP_NAME)
        self.user.groups.add(group)

        # There are some cases where a CompanyUser may be adding themselves
        # and not being invited, so only create an invitation if we can
        # determine who is inviting them.
        if not self.pk and inviting_user:
            invitation = Invitation.objects.create(
                invitee=self.user, inviting_company=self.company,
                inviting_user=inviting_user)
            invitation.save(using=using)
            invitation.send(self)

        return super(CompanyUser, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'company')
        db_table = 'mydashboard_companyuser'

# TODO: This shouldn't be necessary. Find out how to get rid of it
@invitation_context.register(CompanyUser)
def company_user_invitation_context(company_user):
    """Returns a message and the company user."""
    return {"message": " as a(n) Admin for %s." % (company_user.company)}


@receiver(post_delete, sender=CompanyUser,
          dispatch_uid='post_delete_companyuser_signal')
def remove_user_from_group(sender, instance, **kwargs):
    # if a user is not associated with any more companies, we should remove
    # them from the employer group
    if not CompanyUser.objects.filter(user=instance.user):
        instance.user.groups.remove(Group.objects.get(name='Employer'))
        instance.user.save()

# We're a using queue to store messages until they can be read by their handler
# In admin, we check this queue so that warning messages can be sent to the user
# using django.contrib.messages and the request object
# We may be able to implement this behavior in a custom logger
class MessageQueue():
    """
    A queue for storing messages until they can be handled
    Methods should be accessed through the class itself, not instances
    MessageQueue.put(message)
    MessageQueue.send_messages(request)
    """
    message_queue = Queue.Queue()

    @classmethod
    def send_messages(self, request):
        """
        Sends all messages in queue to current user based on input request object
        This currently sends a flash message using django.contrib.messages

        """
        while not self.message_queue.empty():
            messages.warning(request, self.message_queue.get())

    @classmethod
    def put(self, message):
        """Store the input message string in queue to be sent later """
        self.message_queue.put(message)


moc_toggled_on = Signal()
moc_toggled_off = Signal()

# Microsite signals should take Site instances for the sender argument
microsite_disabled = Signal()
microsite_moved = Signal(['old_domain'])


def check_message_queue(f):
    """
    A decorator that will send messages from the signal MessageQueue in
    functions with a request object

    We currently use this in the admin and assume that the 2nd argument on the
    decorated function is a request object. If there is no request object,
    messages are not sent.

    """
    def send_message(self, request=None, *args, **kwargs):
        retval = f(self, request, *args, **kwargs)
        if request is not None:
            MessageQueue.send_messages(request)
        return retval
    return send_message

@receiver(microsite_moved)
def update_canonical_microsites(sender, old_domain, **kwargs):
    """
    Updates company's canonical microsite when an seosite domain is
    changed

    """
    companies = Company.objects.filter(
            canonical_microsite='http://%s' % old_domain)
    # Log messages now because the queryset becomes empty after the update
    for company in companies:
        MessageQueue.put(
          'Canonical microsite for {0} changed from {1} to {2}'.format(
             company.name, old_domain, sender.domain))
    companies.update(canonical_microsite='http://%s' % sender.domain)

@receiver(microsite_disabled)
def remove_canonical_microsite(sender, **kwargs):
    """
    Removes a company's canonical microsite when a SeoSite is disabled

    """
    companies = Company.objects.filter(
            canonical_microsite='http://%s' % sender.domain)
    for company in companies:
        MessageQueue.put(
          'Canonical microsite for {0} removed, default is www.my.jobs'.format(
             company.name, sender.domain))
    companies.update(canonical_microsite=None)


@receiver(post_save, sender=Configuration, dispatch_uid='seo.config_change_monitor')
def config_change_monitor(sender, instance, **kwargs):
    """
    Checks if a configuration change results in a disabled microsite

    """
    for site in instance.seosite_set.all():
        production_configs =  site.configurations.filter(status=2)
        if not production_configs.exists():
            microsite_disabled.send(sender=site)

@receiver(pre_delete, sender=Configuration, dispatch_uid='seo.config_delete_monitor')
def config_delete_monitor(sender, instance, **kwargs):
    """
    Checks if a configuration deletion results in a disabled microsite

    """

    for site in instance.seosite_set.all():
        production_configs =  site.configurations.filter(
                status=2).exclude(id=instance.id)
        if not production_configs.exists():
            microsite_disabled.send(sender=site)

@receiver(pre_delete, sender=SeoSite, dispatch_uid='seo.seosite_delete_monitor')
def seosite_delete_monitor(sender, instance, **kwargs):
    microsite_disabled.send(sender=instance)

@receiver(pre_save, sender=SeoSite, dispatch_uid='seo.seosite_change_monitor')
def seosite_change_monitor(sender, instance, **kwargs):
    """
    Checks for changes to an SeoSite domain and sends the appropriate signal

    """
    pk = instance.pk
    try:
        old_instance = SeoSite.objects.get(id=pk)
    except sender.DoesNotExist:
        return None
    if old_instance.domain != instance.domain:
        microsite_moved.send(sender=instance, old_domain=old_instance.domain)
