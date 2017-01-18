def update_relationships(sender, instance, *args, **kwargs):
    """
    Remove no longer valid DenormalizedSiteRelationships and adds
    new DenormalizedSiteRelationships based on the site relationship that
    changed.

    :param sender: The model that triggered the change (should always be
                   SiteRelationship or a subclass of SiteRelationship).
    :param instance: The SiteRelationship instance that triggered the change.

    """
    # Signals are imported in models.py, which means there are circular
    # imports if these are done at the top of the file.
    from relationships.utils import Graph
    from relationships.models import DenormalizedSiteRelationship

    site = instance.parent

    is_parent_of = DenormalizedSiteRelationship.objects.filter(parent=site)
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
        graph.denormalize_all_relationships(site)
