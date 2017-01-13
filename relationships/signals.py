from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.dispatch import receiver

from relationships.models import DenormalizedSiteRelationship, SiteRelationship
from relationships.utils import Graph


@receiver(post_save, sender=SiteRelationship)
@receiver(post_delete, sender=SiteRelationship)
def update_relationships(sender, instance, *args, **kwargs):
    site = instance.parent

    is_parent_of = DenormalizedSiteRelationship.objects.filter(parent=site)
    list(is_parent_of)
    is_parent_of.delete()

    has_as_child = DenormalizedSiteRelationship.objects.filter(child=site)
    has_as_child = DenormalizedSiteRelationship.objects.filter(
        parent__id__in=has_as_child.values_list('parent_id', flat=True)
    )

    sites_to_update = has_as_child.distinct().values_list('parent', flat=True)
    # Force evaluation here so we have the list before the delete happens.
    sites_to_update = list(sites_to_update)
    sites_to_update.append(site)

    has_as_child.delete()

    graph = Graph()

    for site in sites_to_update:
        graph.normalize_all_relationships(site)
