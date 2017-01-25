from django.contrib import admin

from relationships.models import SiteRelationship, Relationship


class SiteRelationshipAdmin(admin.ModelAdmin):
    fields = ('parent', 'child', 'weight', 'by')

    def get_readonly_fields(self, request, obj=None):
        """
        Prevent editing a SiteRelationship after it is created.

        """
        if obj:
            return self.fields
        return self.readonly_fields


admin.site.register(Relationship)
admin.site.register(SiteRelationship, SiteRelationshipAdmin)
