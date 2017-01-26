import json

from django.core.files.base import ContentFile
from django.core.exceptions import SuspiciousOperation
from django.db import models
from django.db.models.loading import get_model

from myreports.helpers import serialize, determine_user_type
from myreports.datasources import ds_json_drivers
from myreports.report_configuration import (
    ReportConfiguration, ColumnConfiguration)
from myreports.result_encoder import report_hook, ReportJsonEncoder
from mypartners.models import SearchParameterManager


class Report(models.Model):
    """
    Models a Report which can be serialized in various formats.

    A report instance can access it's results in three ways:
        `json`: returns a JSON string of the results
        `python`: returns a `dict` of the results
        `queryset`: returns a queryset obtained by re-running `from_search`
                    with the report's parameters. Useful for when you need to
                    use attributes from a related model's instances (eg.
                    `referrals` from the `ContactRecord` model).
    """
    name = models.CharField(max_length=50)
    created_by = models.ForeignKey(
        'myjobs.User', null=True, on_delete=models.SET_NULL)
    owner = models.ForeignKey('seo.Company')
    created_on = models.DateTimeField(auto_now_add=True)
    order_by = models.CharField(max_length=50, blank=True, default='')
    app = models.CharField(default='mypartners', max_length=50)
    model = models.CharField(default='contactrecord', max_length=50)
    # included columns and sort order
    values = models.CharField(max_length=500, default='[]')
    # json encoded string of the filters used to filter
    filters = models.TextField(default="{}")
    results = models.FileField(upload_to='reports')

    company_ref = 'owner'

    objects = SearchParameterManager()

    def __init__(self, *args, **kwargs):
        super(Report, self).__init__(*args, **kwargs)
        self._results = '{}'

        if self.results:
            try:
                self._results = self.results.read()
            except IOError:
                # If we are here, the file can't be found, which is usually the
                # case when testing locally and pointing to
                # QC/Staging/Production.
                pass

    @property
    def json(self):
        return self._results

    @property
    def python(self):
        return json.loads(self._results)

    @property
    def queryset(self):
        model = get_model(self.app, self.model)
        return model.objects.from_search(self.owner, self.filters)

    def __unicode__(self):
        return self.name

    def regenerate(self):
        """Regenerate the report file if it doesn't already exist on disk."""
        contents = serialize('json', self.queryset)
        results = ContentFile(contents)

        if self.results:
            self.results.delete()

        self.results.save('%s-%s.json' % (self.name, self.pk), results)
        self._results = contents


class UserTypeManager(models.Manager):
    def for_user(self, user):
        user_type = determine_user_type(user)
        if user_type is None:
            return None
        return UserType.objects.filter(user_type=user_type,
                                       is_active=True).first()


class UserType(models.Model):
    user_type = models.CharField(max_length=10)
    is_active = models.BooleanField(default=False)
    reporting_types = models.ManyToManyField(
        'ReportingType', through='UserReportingTypes')
    objects = UserTypeManager()

    def __unicode__(self):
        return self.user_type


class ReportingTypeManager(models.Manager):
    def active_for_user(self, user):
        user_type = UserType.objects.for_user(user)
        return (ReportingType.objects.filter(is_active=True)
                .filter(userreportingtypes__is_active=True,
                        userreportingtypes__user_type=user_type))


class ReportingType(models.Model):
    reporting_type = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    report_types = models.ManyToManyField(
        'ReportType', through='ReportingTypeReportTypes')
    is_active = models.BooleanField(default=False)
    objects = ReportingTypeManager()

    def __unicode__(self):
        return self.reporting_type


class UserReportingTypes(models.Model):
    user_type = models.ForeignKey('UserType')
    reporting_type = models.ForeignKey('ReportingType')
    is_active = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s to %s" % (self.user_type, self.reporting_type)


class ReportTypeManager(models.Manager):
    def active_for_reporting_type(self, reporting_type):
        query_filter = dict(
            is_active=True,
            reportingtypereporttypes__reporting_type=reporting_type,
            reportingtypereporttypes__is_active=True)
        return ReportType.objects.filter(**query_filter)


class ReportType(models.Model):
    report_type = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    data_types = models.ManyToManyField(
        'DataType', through='ReportTypeDataTypes')
    is_active = models.BooleanField(default=False)
    datasource = models.CharField(max_length=50, default='')
    objects = ReportTypeManager()

    def __unicode__(self):
        return unicode((self.pk, self.report_type))


class ReportingTypeReportTypes(models.Model):
    reporting_type = models.ForeignKey('ReportingType')
    report_type = models.ForeignKey('ReportType')
    is_active = models.BooleanField(default=False)


class DataTypeManager(models.Manager):
    def active_for_report_type(self, report_type):
        query_filter = dict(
            is_active=True,
            reporttypedatatypes__configuration__is_active=True,
            reporttypedatatypes__report_type=report_type,
            reporttypedatatypes__is_active=True)
        return DataType.objects.filter(**query_filter)


class DataType(models.Model):
    data_type = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    is_active = models.BooleanField(default=False)
    objects = DataTypeManager()


class ReportTypeDataTypesManager(models.Manager):
    def build_choices(
            self, user, reporting_type_name, report_type_name, data_type_name):

        if not user or not user.pk or user.is_anonymous():
            raise SuspiciousOperation("No user provided.")

        reporting_types = (
            ReportingType.objects.active_for_user(user)
            .order_by('description'))
        selected_reporting_type = self.select_best(
            reporting_types, 'reporting_type', reporting_type_name)

        report_types = (
            ReportType.objects.active_for_reporting_type(
                selected_reporting_type)
            .order_by('description'))
        selected_report_type = self.select_best(
            report_types, 'report_type', report_type_name)

        data_types = (
            DataType.objects.active_for_report_type(selected_report_type)
            .order_by('description'))
        selected_data_type = self.select_best(
            data_types, 'data_type', data_type_name)

        return {
            'reporting_types': reporting_types,
            'selected_reporting_type': selected_reporting_type,
            'report_types': report_types,
            'selected_report_type': selected_report_type,
            'data_types': data_types,
            'selected_data_type': selected_data_type,
        }

    def select_best(self, choices, name_field, selected_name):
        choices_list = list(choices)
        for choice in choices_list:
            if getattr(choice, name_field) == selected_name:
                return choice

        if len(choices_list) > 0:
            return choices_list[0]
        else:
            return None

    def first_active_for_report_type_data_type(self, report_type, data_type):
        query_filter = dict(
            report_type=report_type,
            data_type=data_type,
            is_active=True)
        report_datas = list(ReportTypeDataTypes.objects.filter(**query_filter))
        if len(report_datas) > 0:
            return report_datas[0]
        else:
            return None


class ReportTypeDataTypes(models.Model):
    report_type = models.ForeignKey('ReportType')
    data_type = models.ForeignKey('DataType')
    is_active = models.BooleanField(default=False)
    configuration = models.ForeignKey('Configuration', null=True)
    objects = ReportTypeDataTypesManager()

    def __unicode__(self):
        return "%s %s" % (self.report_type.report_type,
                          self.data_type.data_type)


class Configuration(models.Model):
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)

    def build_configuration(self):
        return ReportConfiguration([
            ColumnConfiguration(
                column=cm.column_name,
                alias=cm.alias,
                format=cm.output_format,
                filter_interface=cm.filter_interface_type,
                filter_display=cm.filter_interface_display,
                help=cm.has_help)
            for cm in (
                self.configurationcolumn_set
                .filter(is_active=True)
                .order_by('order'))])

    def __unicode__(self):
        return self.name


class ReportPresentationManager(models.Manager):
    def active_for_report_type_data_type(self, rtdt):
        query_filter = dict(
            presentation_type__is_active=True,
            report_data=rtdt,
            is_active=True)
        return ReportPresentation.objects.filter(**query_filter)


class ReportPresentation(models.Model):
    report_data = models.ForeignKey('ReportTypeDataTypes')
    presentation_type = models.ForeignKey('PresentationType')
    display_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)
    objects = ReportPresentationManager()


class PresentationType(models.Model):
    presentation_type = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    is_active = models.BooleanField(default=False)


class Column(models.Model):
    table_name = models.CharField(max_length=50)
    column_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)


class ConfigurationColumnManager(models.Manager):
    def active_for_report_data(self, report_data):
        return (ConfigurationColumn.objects
                .filter(configuration__reporttypedatatypes=report_data)
                .filter(is_active=True)
                .select_related())


class ConfigurationColumn(models.Model):
    configuration = models.ForeignKey(Configuration)

    order = models.IntegerField(default=100)
    column_name = models.CharField(max_length=50, default='')
    output_format = models.CharField(max_length=50, default='')
    filter_interface_type = models.CharField(max_length=50, null=True)
    filter_interface_display = models.CharField(max_length=50, null=True)
    has_help = models.BooleanField(default=False)

    alias = models.CharField(max_length=100)
    multi_value_expansion = models.PositiveSmallIntegerField()
    filter_only = models.BooleanField(default=False)
    default_value = models.CharField(max_length=500, blank=True, default="")
    is_active = models.BooleanField(default=False)
    objects = ConfigurationColumnManager()

    def __unicode__(self):
        return self.column_name


class DynamicReport(models.Model):
    """
    Models a Report which was generated from a Configuration.

    The report can be serialized in various formats.

    A report instance can access it's results in three ways:
        `json`: returns a JSON string of the results
        `python`: returns a `dict` of the results
        `queryset`: returns a queryset obtained by re-running `from_search`
                    with the report's parameters. Useful for when you need to
                    use attributes from a related model's instances (eg.
                    `referrals` from the `ContactRecord` model).
    """
    name = models.CharField(max_length=50)
    created_by = models.ForeignKey(
        'myjobs.User', null=True, on_delete=models.SET_NULL)
    created_on = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('seo.Company')
    report_data = models.ForeignKey('myreports.ReportTypeDataTypes', null=True)
    filters = models.TextField(default="{}")
    results = models.FileField(upload_to='reports')

    company_ref = 'owner'

    objects = SearchParameterManager()

    def __init__(self, *args, **kwargs):
        super(DynamicReport, self).__init__(*args, **kwargs)
        self._results = '{}'

        if self.results:
            try:
                self._results = self.results.read()
            except IOError:
                # If we are here, the file can't be found, which is usually the
                # case when testing locally and pointing to
                # QC/Staging/Production.
                pass

    @property
    def json(self):
        return self._results

    @property
    def python(self):
        return json.loads(self._results, object_hook=report_hook)

    def regenerate(self):
        report_type = self.report_data.report_type
        data_type = self.report_data.data_type

        driver = ds_json_drivers[report_type.datasource]
        data_type_name = data_type.data_type
        data = driver.run(data_type_name, self.owner, self.filters, "[]")

        contents = json.dumps(data, cls=ReportJsonEncoder)
        results = ContentFile(contents)

        if self.results:
            self.results.delete()

        self.results.save('%s-%s.json' % (self.name, self.pk), results)
        self._results = contents
        self.save()
