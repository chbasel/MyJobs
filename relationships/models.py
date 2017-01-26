from django.db import models
from django.db.models.signals import post_save
from django.db.models.signals import post_delete

from relationships.signals import update_relationships


class EditingNotAllowed(Exception):
    message = "Editing of this object is not allowed."


class Relationship(models.Model):
    type = models.CharField(max_length=255)

    def __unicode__(self):
        return self.type


class BaseRelationship(models.Model):
    weight = models.FloatField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return '%s -- %s --> %s' % (self.parent.domain, self.by.type,
                                    self.child.domain)


class SiteRelationship(BaseRelationship):
    parent = models.ForeignKey('seo.SeoSite', blank=False,
                               related_name='child_set')
    child = models.ForeignKey('seo.SeoSite', blank=False,
                              related_name='parent_set')
    by = models.ForeignKey('Relationship')

    class Meta:
        unique_together = ('parent', 'child', 'by')

    def save(self, **kwargs):
        if self.pk:
            raise EditingNotAllowed

        return super(SiteRelationship, self).save(**kwargs)


post_save.connect(update_relationships, sender=SiteRelationship)
post_delete.connect(update_relationships, sender=SiteRelationship)


class DenormalizedSiteRelationship(BaseRelationship):
    parent = models.ForeignKey('seo.SeoSite', blank=False,
                               related_name='normalized_child_set')
    child = models.ForeignKey('seo.SeoSite', blank=False,
                              related_name='normalized_parent_set')
    by = models.ForeignKey('Relationship',
                           related_name='normalized_by_set')
    depth = models.IntegerField()

