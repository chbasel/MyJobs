from django.contrib import admin

from moc_coding.models import CustomCareer


class CustomCareerAdmin(admin.ModelAdmin):
    list_display = ('moc', 'onet', 'content_object')
    search_fields = ['moc__code', 'moc__title', 'moc__branch', 'onet__code']
    

admin.site.register(CustomCareer, CustomCareerAdmin)
