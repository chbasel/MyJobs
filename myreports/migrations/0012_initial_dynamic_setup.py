# -*- coding: utf-8 -*-
# from south.utils import datetime_utils as datetime
# from south.db import db
from south.v2 import DataMigration
# from django.db import models


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.

        orm["myreports.UserType"].objects.all().delete()
        ut_emp = orm["myreports.UserType"].objects.create(
            user_type="EMPLOYER",
            is_active=True)
        orm["myreports.UserType"].objects.create(
            user_type="STAFF",
            is_active=True)

        orm["myreports.ReportingType"].objects.all().delete()
        rit_prm = orm["myreports.ReportingType"].objects.create(
            reporting_type="prm",
            description="PRM Reports", is_active=True)

        orm["myreports.UserReportingTypes"].objects.all().delete()
        orm["myreports.UserReportingTypes"].objects.create(
            user_type=ut_emp, reporting_type=rit_prm, is_active=True)

        orm["myreports.ReportType"].objects.all().delete()
        rt_partners = orm["myreports.ReportType"].objects.create(
            report_type="partners",
            description="Partners Report",
            datasource="partners", is_active=True)
        rt_con = orm["myreports.ReportType"].objects.create(
            report_type="contacts",
            description="Contacts Report",
            datasource="contacts", is_active=True)
        rt_comm = orm["myreports.ReportType"].objects.create(
            report_type="communication-records",
            description="Communication Records Report",
            datasource="comm_records", is_active=True)

        orm["myreports.ReportingTypeReportTypes"].objects.all().delete()
        orm["myreports.ReportingTypeReportTypes"].objects.create(
            report_type=rt_partners, reporting_type=rit_prm, is_active=True)
        orm["myreports.ReportingTypeReportTypes"].objects.create(
            report_type=rt_con, reporting_type=rit_prm, is_active=True)
        orm["myreports.ReportingTypeReportTypes"].objects.create(
            report_type=rt_comm, reporting_type=rit_prm, is_active=True)

        orm["myreports.DataType"].objects.all().delete()
        dt_unagg = orm["myreports.DataType"].objects.create(
            data_type="unaggregated",
            description="Unaggregated", is_active=True)

        orm["myreports.PresentationType"].objects.all().delete()
        pre_csv = orm["myreports.PresentationType"].objects.create(
            presentation_type="csv", description="CSV", is_active=True)
        pre_xlsx = orm["myreports.PresentationType"].objects.create(
            presentation_type="xlsx", description="Excel xlsx", is_active=True)

        orm["myreports.Configuration"].objects.all().delete()
        con_con = orm["myreports.Configuration"].objects.create(
            name="Contact Basic Report", is_active=True)
        con_part = orm["myreports.Configuration"].objects.create(
            name="Partner Basic Report", is_active=True)
        con_comm = orm["myreports.Configuration"].objects.create(
            name="Communication Records Basic Report", is_active=True)

        orm["myreports.ConfigurationColumn"].objects.all().delete()
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="date",
            alias='Date',
            order=100,
            configuration=con_con,
            output_format="us_datetime",
            filter_interface_type='date_range',
            filter_interface_display='Date',
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="locations",
            alias='Location',
            order=101,
            output_format="city_state_list",
            filter_interface_type='city_state',
            filter_interface_display='Location',
            configuration=con_con,
            multi_value_expansion=False,
            has_help=True, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="tags",
            alias='Tags',
            order=102,
            output_format="tags_list",
            filter_interface_type='tags',
            filter_interface_display='Tags',
            configuration=con_con,
            multi_value_expansion=False,
            has_help=True, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="partner",
            alias='Partners',
            order=103,
            output_format="text",
            filter_interface_type='search_multiselect',
            filter_interface_display='Partners',
            configuration=con_con,
            multi_value_expansion=False,
            has_help=True, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="name",
            alias="Name",
            order=104,
            output_format="text",
            configuration=con_con,
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="email",
            alias="Email",
            order=105,
            output_format="text",
            configuration=con_con,
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="phone",
            alias="Phone",
            order=106,
            output_format="text",
            configuration=con_con,
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="notes",
            alias="Notes",
            order=107,
            output_format="text",
            configuration=con_con,
            multi_value_expansion=False, is_active=True)

        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="date",
            alias="Date",
            order=100,
            configuration=con_part,
            output_format="us_datetime",
            filter_interface_type='date_range',
            filter_interface_display='Date',
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            order=101,
            column_name="locations",
            alias='Contact Location',
            filter_interface_type='city_state',
            filter_interface_display='Contact Location',
            filter_only=True,
            configuration=con_part,
            multi_value_expansion=False,
            has_help=True, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="tags",
            alias='Tags',
            order=102,
            output_format="tags_list",
            filter_interface_type='tags',
            filter_interface_display='Tags',
            configuration=con_part,
            multi_value_expansion=False,
            has_help=True, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="uri",
            alias='URL',
            order=103,
            output_format="text",
            filter_interface_type='search_select',
            filter_interface_display='URL',
            configuration=con_part,
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="data_source",
            alias='Source',
            order=104,
            output_format="text",
            filter_interface_type='search_select',
            filter_interface_display='Source',
            configuration=con_part,
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="name",
            alias="Name",
            order=105,
            output_format="text",
            configuration=con_part,
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="primary_contact",
            alias="Primary Contact",
            order=106,
            output_format="text",
            configuration=con_part,
            multi_value_expansion=False, is_active=True)

        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="date_time",
            alias="Date of Communication",
            order=107,
            configuration=con_comm,
            output_format="us_datetime",
            filter_interface_type='date_range',
            filter_interface_display='Date',
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            order=108,
            column_name="locations",
            alias='Contact Location',
            filter_interface_type='city_state',
            filter_interface_display='Contact Location',
            filter_only=True,
            configuration=con_comm,
            multi_value_expansion=False,
            has_help=True, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="tags",
            alias='Tags',
            order=109,
            output_format="tags_list",
            filter_interface_type='tags',
            filter_interface_display='Tags',
            configuration=con_comm,
            multi_value_expansion=False,
            has_help=True, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="communication_type",
            alias='Communication Type',
            order=110,
            filter_interface_type='search_multiselect',
            filter_interface_display='Communication Type',
            configuration=con_comm,
            output_format="comm_types_list",
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="partner",
            alias='Partners',
            order=111,
            output_format="text",
            filter_interface_type='search_multiselect',
            filter_interface_display='Partners',
            configuration=con_comm,
            multi_value_expansion=False,
            has_help=True, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="contact",
            alias='Contacts',
            order=112,
            output_format="text",
            filter_interface_type='search_multiselect',
            filter_interface_display='Contacts',
            configuration=con_comm,
            multi_value_expansion=False,
            has_help=True, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="contact_email",
            alias="Contact Email",
            order=113,
            output_format="text",
            configuration=con_comm,
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="contact_phone",
            alias="Contact Phone",
            order=114,
            configuration=con_comm,
            output_format="text",
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="created_on",
            alias="Created On",
            order=115,
            configuration=con_comm,
            output_format="us_date",
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="created_by",
            alias="Created By",
            order=116,
            configuration=con_comm,
            output_format="text",
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="job_applications",
            alias="Job Applications",
            order=117,
            output_format="text",
            configuration=con_comm,
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="job_hires",
            alias="Job Hires",
            order=118,
            output_format="text",
            configuration=con_comm,
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="job_id",
            alias="Job ID",
            order=119,
            output_format="text",
            configuration=con_comm,
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="job_interviews",
            alias="Job Interviews",
            order=120,
            output_format="text",
            configuration=con_comm,
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="length",
            alias="Length",
            order=122,
            output_format="text",
            configuration=con_comm,
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="location",
            alias="Meeting Location",
            order=123,
            output_format="text",
            configuration=con_comm,
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="notes",
            alias="Notes",
            order=124,
            output_format="text",
            configuration=con_comm,
            multi_value_expansion=False, is_active=True)
        orm["myreports.ConfigurationColumn"].objects.create(
            column_name="subject",
            alias="Subject",
            order=125,
            output_format="text",
            configuration=con_comm,
            multi_value_expansion=False, is_active=True)

        orm["myreports.ReportTypeDataTypes"].objects.all().delete()
        rtdt_con_unagg = orm["myreports.ReportTypeDataTypes"].objects.create(
            report_type=rt_con, data_type=dt_unagg, configuration=con_con,
            is_active=True)
        rtdt_part_unagg = orm["myreports.ReportTypeDataTypes"].objects.create(
            report_type=rt_partners, data_type=dt_unagg,
            configuration=con_part, is_active=True)
        rtdt_comm_unagg = orm["myreports.ReportTypeDataTypes"].objects.create(
            report_type=rt_comm, data_type=dt_unagg, configuration=con_comm,
            is_active=True)

        orm["myreports.ReportPresentation"].objects.all().delete()
        orm["myreports.ReportPresentation"].objects.create(
            presentation_type=pre_csv,
            display_name="Contact CSV",
            report_data=rtdt_con_unagg, is_active=True)
        orm["myreports.ReportPresentation"].objects.create(
            presentation_type=pre_csv,
            display_name="Partner CSV",
            report_data=rtdt_part_unagg, is_active=True)
        orm["myreports.ReportPresentation"].objects.create(
            presentation_type=pre_csv,
            display_name="Communication Record CSV",
            report_data=rtdt_comm_unagg, is_active=True)
        orm["myreports.ReportPresentation"].objects.create(
            presentation_type=pre_xlsx,
            display_name="Contact Excel Spreadsheet",
            report_data=rtdt_con_unagg, is_active=True)
        orm["myreports.ReportPresentation"].objects.create(
            presentation_type=pre_xlsx,
            display_name="Partner Excel Spreadsheet",
            report_data=rtdt_part_unagg, is_active=True)
        orm["myreports.ReportPresentation"].objects.create(
            presentation_type=pre_xlsx,
            display_name="Communication Record Excel Spreadsheet",
            report_data=rtdt_comm_unagg, is_active=True)

    def backwards(self, orm):
        "Write your backwards methods here."
        raise RuntimeError(
            "Cannot reverse this migration. " +
            "This migration could delete or invalidate customer data.")

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'myjobs.activity': {
            'Meta': {'object_name': 'Activity'},
            'app_access': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myjobs.AppAccess']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'myjobs.appaccess': {
            'Meta': {'object_name': 'AppAccess'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'myjobs.role': {
            'Meta': {'unique_together': "(('company', 'name'),)", 'object_name': 'Role'},
            'activities': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['myjobs.Activity']", 'symmetrical': 'False'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['seo.Company']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'myjobs.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deactivate_type': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '11'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'gravatar': ('django.db.models.fields.EmailField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_reserve': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_disabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'last_response': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'opt_in_employers': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'opt_in_myjobs': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'password_change': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'profile_completion': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['myjobs.Role']", 'symmetrical': 'False'}),
            'source': ('django.db.models.fields.CharField', [], {'default': "'https://secure.my.jobs'", 'max_length': '255'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'America/New_York'", 'max_length': '255'}),
            'user_guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"})
        },
        u'myreports.column': {
            'Meta': {'object_name': 'Column'},
            'column_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'table_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'myreports.configuration': {
            'Meta': {'object_name': 'Configuration'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'myreports.configurationcolumn': {
            'Meta': {'object_name': 'ConfigurationColumn'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'column_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'configuration': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myreports.Configuration']"}),
            'default_value': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500', 'blank': 'True'}),
            'filter_interface_display': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'filter_interface_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'filter_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_help': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'multi_value_expansion': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'output_format': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'})
        },
        u'myreports.datatype': {
            'Meta': {'object_name': 'DataType'},
            'data_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'myreports.dynamicreport': {
            'Meta': {'object_name': 'DynamicReport'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myjobs.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'filters': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['seo.Company']"}),
            'report_data': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myreports.ReportTypeDataTypes']", 'null': 'True'}),
            'results': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        u'myreports.presentationtype': {
            'Meta': {'object_name': 'PresentationType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'presentation_type': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'myreports.report': {
            'Meta': {'object_name': 'Report'},
            'app': ('django.db.models.fields.CharField', [], {'default': "'mypartners'", 'max_length': '50'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myjobs.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'filters': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'default': "'contactrecord'", 'max_length': '50'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'order_by': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['seo.Company']"}),
            'results': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'values': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '500'})
        },
        u'myreports.reportingtype': {
            'Meta': {'object_name': 'ReportingType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'report_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['myreports.ReportType']", 'through': u"orm['myreports.ReportingTypeReportTypes']", 'symmetrical': 'False'}),
            'reporting_type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'myreports.reportingtypereporttypes': {
            'Meta': {'object_name': 'ReportingTypeReportTypes'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'report_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myreports.ReportType']"}),
            'reporting_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myreports.ReportingType']"})
        },
        u'myreports.reportpresentation': {
            'Meta': {'object_name': 'ReportPresentation'},
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'presentation_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myreports.PresentationType']"}),
            'report_data': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myreports.ReportTypeDataTypes']"})
        },
        u'myreports.reporttype': {
            'Meta': {'object_name': 'ReportType'},
            'data_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['myreports.DataType']", 'through': u"orm['myreports.ReportTypeDataTypes']", 'symmetrical': 'False'}),
            'datasource': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'report_type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'myreports.reporttypedatatypes': {
            'Meta': {'object_name': 'ReportTypeDataTypes'},
            'configuration': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myreports.Configuration']", 'null': 'True'}),
            'data_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myreports.DataType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'report_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myreports.ReportType']"})
        },
        u'myreports.userreportingtypes': {
            'Meta': {'object_name': 'UserReportingTypes'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reporting_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myreports.ReportingType']"}),
            'user_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myreports.UserType']"})
        },
        u'myreports.usertype': {
            'Meta': {'object_name': 'UserType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reporting_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['myreports.ReportingType']", 'through': u"orm['myreports.UserReportingTypes']", 'symmetrical': 'False'}),
            'user_type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'postajob.package': {
            'Meta': {'object_name': 'Package'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'postajob.sitepackage': {
            'Meta': {'object_name': 'SitePackage', '_ormbases': [u'postajob.Package']},
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['seo.Company']", 'null': 'True', 'blank': 'True'}),
            u'package_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['postajob.Package']", 'unique': 'True', 'primary_key': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['seo.SeoSite']", 'null': 'True', 'symmetrical': 'False'})
        },
        u'seo.atssourcecode': {
            'Meta': {'object_name': 'ATSSourceCode'},
            'ats_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'value': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'})
        },
        u'seo.billboardimage': {
            'Meta': {'object_name': 'BillboardImage'},
            'copyright_info': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'logo_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'sponsor_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'seo.businessunit': {
            'Meta': {'object_name': 'BusinessUnit'},
            'associated_jobs': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date_crawled': ('django.db.models.fields.DateTimeField', [], {}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {}),
            'enable_markdown': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'federal_contractor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'primary_key': 'True'}),
            'ignore_includeinindex': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site_packages': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['postajob.SitePackage']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'title_slug': ('django.db.models.fields.SlugField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'})
        },
        u'seo.company': {
            'Meta': {'ordering': "['name']", 'unique_together': "(('name', 'user_created'),)", 'object_name': 'Company'},
            'app_access': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['myjobs.AppAccess']", 'symmetrical': 'False', 'blank': 'True'}),
            'canonical_microsite': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'company_slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'digital_strategies_customer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enhanced': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_source_ids': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['seo.BusinessUnit']", 'symmetrical': 'False'}),
            'linkedin_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'logo_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'member': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'og_img': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'posting_access': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'prm_saved_search_sites': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['seo.SeoSite']", 'null': 'True', 'blank': 'True'}),
            'product_access': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site_package': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.SitePackage']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'user_created': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'seo.configuration': {
            'Meta': {'object_name': 'Configuration'},
            'backgroundColor': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'body': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'browse_city_order': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'browse_city_show': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'browse_city_text': ('django.db.models.fields.CharField', [], {'default': "'City'", 'max_length': '50'}),
            'browse_company_order': ('django.db.models.fields.IntegerField', [], {'default': '7'}),
            'browse_company_show': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'browse_company_text': ('django.db.models.fields.CharField', [], {'default': "'Company'", 'max_length': '50'}),
            'browse_country_order': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'browse_country_show': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'browse_country_text': ('django.db.models.fields.CharField', [], {'default': "'Country'", 'max_length': '50'}),
            'browse_facet_order': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'browse_facet_order_2': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'browse_facet_order_3': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'browse_facet_order_4': ('django.db.models.fields.IntegerField', [], {'default': '4'}),
            'browse_facet_show': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'browse_facet_show_2': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'browse_facet_show_3': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'browse_facet_show_4': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'browse_facet_text': ('django.db.models.fields.CharField', [], {'default': "'Job Profiles'", 'max_length': '50'}),
            'browse_facet_text_2': ('django.db.models.fields.CharField', [], {'default': "'Job Profiles'", 'max_length': '50'}),
            'browse_facet_text_3': ('django.db.models.fields.CharField', [], {'default': "'Job Profiles'", 'max_length': '50'}),
            'browse_facet_text_4': ('django.db.models.fields.CharField', [], {'default': "'Job Profiles'", 'max_length': '50'}),
            'browse_moc_order': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'browse_moc_show': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'browse_moc_text': ('django.db.models.fields.CharField', [], {'default': "'Military Titles'", 'max_length': '50'}),
            'browse_state_order': ('django.db.models.fields.IntegerField', [], {'default': '4'}),
            'browse_state_show': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'browse_state_text': ('django.db.models.fields.CharField', [], {'default': "'State'", 'max_length': '50'}),
            'browse_title_order': ('django.db.models.fields.IntegerField', [], {'default': '6'}),
            'browse_title_show': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'browse_title_text': ('django.db.models.fields.CharField', [], {'default': "'Title'", 'max_length': '50'}),
            'company_tag': ('django.db.models.fields.CharField', [], {'default': "'careers'", 'max_length': '50'}),
            'defaultBlurb': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'defaultBlurbTitle': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'directemployers_link': ('django.db.models.fields.URLField', [], {'default': "'http://directemployers.org'", 'max_length': '200'}),
            'doc_type': ('django.db.models.fields.CharField', [], {'default': '\'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\'', 'max_length': '255'}),
            'facet_tag': ('django.db.models.fields.CharField', [], {'default': "'new-jobs'", 'max_length': '50'}),
            'fontColor': ('django.db.models.fields.CharField', [], {'default': "'666666'", 'max_length': '6'}),
            'footer': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True'}),
            'header': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'home_page_template': ('django.db.models.fields.CharField', [], {'default': "'home_page/home_page_listing.html'", 'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '16'}),
            'location_tag': ('django.db.models.fields.CharField', [], {'default': "'jobs'", 'max_length': '50'}),
            'meta': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'moc_helptext': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'moc_label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'moc_placeholder': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'moc_tag': ('django.db.models.fields.CharField', [], {'default': "'vet-jobs'", 'max_length': '50'}),
            'num_filter_items_to_show': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'num_job_items_to_show': ('django.db.models.fields.IntegerField', [], {'default': '15'}),
            'num_subnav_items_to_show': ('django.db.models.fields.IntegerField', [], {'default': '9'}),
            'percent_featured': ('django.db.models.fields.DecimalField', [], {'default': "'0.5'", 'max_digits': '3', 'decimal_places': '2'}),
            'primaryColor': ('django.db.models.fields.CharField', [], {'default': "'990000'", 'max_length': '6'}),
            'publisher': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'revision': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'show_home_microsite_carousel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_home_social_footer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_saved_search_widget': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_social_footer': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'title_tag': ('django.db.models.fields.CharField', [], {'default': "'jobs-in'", 'max_length': '50'}),
            'use_secure_blocks': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'view_all_jobs_detail': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'what_helptext': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'what_label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'what_placeholder': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'where_helptext': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'where_label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'where_placeholder': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'wide_footer': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'wide_header': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'seo.customfacet': {
            'Meta': {'object_name': 'CustomFacet'},
            'always_show': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'blurb': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'business_units': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['seo.BusinessUnit']", 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '800', 'null': 'True', 'blank': 'True'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '800', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '800', 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'onet': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'querystring': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'saved_querystring': ('django.db.models.fields.CharField', [], {'max_length': '10000', 'blank': 'True'}),
            'show_blurb': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_production': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '800', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '800', 'null': 'True', 'blank': 'True'}),
            'url_slab': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'seo.googleanalytics': {
            'Meta': {'object_name': 'GoogleAnalytics'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'web_property_id': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'seo.googleanalyticscampaign': {
            'Meta': {'object_name': 'GoogleAnalyticsCampaign'},
            'campaign_content': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'campaign_medium': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'campaign_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'campaign_source': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'campaign_term': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'})
        },
        u'seo.seosite': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'SeoSite', '_ormbases': [u'sites.Site']},
            'ats_source_codes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['seo.ATSSourceCode']", 'null': 'True', 'blank': 'True'}),
            'billboard_images': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['seo.BillboardImage']", 'null': 'True', 'blank': 'True'}),
            'business_units': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['seo.BusinessUnit']", 'null': 'True', 'blank': 'True'}),
            'canonical_company': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'canonical_company_for'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['seo.Company']"}),
            'configurations': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['seo.Configuration']", 'symmetrical': 'False', 'blank': 'True'}),
            'email_domain': ('django.db.models.fields.CharField', [], {'default': "'my.jobs'", 'max_length': '255'}),
            'facets': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['seo.CustomFacet']", 'null': 'True', 'through': u"orm['seo.SeoSiteFacet']", 'blank': 'True'}),
            'featured_companies': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['seo.Company']", 'null': 'True', 'blank': 'True'}),
            'google_analytics': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['seo.GoogleAnalytics']", 'null': 'True', 'blank': 'True'}),
            'google_analytics_campaigns': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['seo.GoogleAnalyticsCampaign']", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True'}),
            'microsite_carousel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social_links.MicrositeCarousel']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'parent_site': ('seo.models.NonChainedForeignKey', [], {'blank': 'True', 'related_name': "'child_sites'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['seo.SeoSite']"}),
            'postajob_filter_type': ('django.db.models.fields.CharField', [], {'default': "'this site only'", 'max_length': '255'}),
            'site_description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'site_heading': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'site_package': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.SitePackage']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            u'site_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sites.Site']", 'unique': 'True', 'primary_key': 'True'}),
            'site_tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['seo.SiteTag']", 'null': 'True', 'blank': 'True'}),
            'site_title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'special_commitments': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['seo.SpecialCommitment']", 'null': 'True', 'blank': 'True'}),
            'view_sources': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['seo.ViewSource']", 'null': 'True', 'blank': 'True'})
        },
        u'seo.seositefacet': {
            'Meta': {'object_name': 'SeoSiteFacet'},
            'boolean_operation': ('django.db.models.fields.CharField', [], {'default': "'or'", 'max_length': '3', 'db_index': 'True'}),
            'customfacet': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['seo.CustomFacet']"}),
            'facet_group': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'facet_type': ('django.db.models.fields.CharField', [], {'default': "'STD'", 'max_length': '4', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'seosite': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['seo.SeoSite']"})
        },
        u'seo.sitetag': {
            'Meta': {'object_name': 'SiteTag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site_tag': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'tag_navigation': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'seo.specialcommitment': {
            'Meta': {'object_name': 'SpecialCommitment'},
            'commit': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'seo.viewsource': {
            'Meta': {'object_name': 'ViewSource'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'view_source': ('django.db.models.fields.IntegerField', [], {'default': "''", 'max_length': '20'})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'social_links.micrositecarousel': {
            'Meta': {'object_name': 'MicrositeCarousel'},
            'carousel_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'display_rows': ('django.db.models.fields.IntegerField', [], {}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_all_sites': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'link_sites': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'linked_carousel'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['seo.SeoSite']"})
        }
    }

    complete_apps = ['myreports']
    symmetrical = True
