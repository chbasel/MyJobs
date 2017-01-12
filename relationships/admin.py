from django.contrib import admin

from relationships.models import SiteRelationship, Relationship


class SiteRelationshipAdmin(admin.ModelAdmin):
    fields = ('parent', 'child', 'weight', 'by')


admin.site.register(Relationship)
admin.site.register(SiteRelationship, SiteRelationshipAdmin)
