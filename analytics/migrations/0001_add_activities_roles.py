# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        """
        create default activities/app access for analytics module


        """

        analytics = orm['myjobs.AppAccess'].objects.create(name="Analytics")
        orm['myjobs.Activity'].objects.create(
            name="view analytics",
            description="Access Analytics Graphs and Reporting.",
            app_access=analytics
        )

    def backwards(self, orm):
        """
        delete activites/app access for module


        """
        analytics = orm['myjobs.AppAccess'].objects.get(name="Analytics")
        orm['myjobs.Activity'].objects.filter(app_access=analytics).delete()
        analytics.delete()

    models = {}

    complete_apps = ['analytics']
    symmetrical = True
