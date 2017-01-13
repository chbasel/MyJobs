import logging
from collections import defaultdict

from relationships.models import SiteRelationship, DenormalizedSiteRelationship
from seo.models import SeoSite


logger = logging.getLogger(__name__)


class Graph(object):
    __graph__ = None

    def __init__(self):
        self.build()

    def build(self):
        graph = defaultdict(lambda: defaultdict(list))

        site_relationships = SiteRelationship.objects.all()
        related = ('parent', 'child')
        for relationship in site_relationships.select_related(*related):
            parent_id = relationship.parent.id
            child_id = relationship.child.id
            by = relationship.by.id
            weight = relationship.weight
            graph[parent_id][by].append((child_id, weight, by))

        self.__graph__ = graph

    def children_by_depth(self, parent_id, by=None, depth=1):
        children_by_depth = {}
        current = (parent_id, )

        for current_depth in range(0, depth):
            immediate_children = []

            for site_id in set(current):
                immediate_children += self.immediate_children(site_id, by=by)

            children_by_depth[current_depth + 1] = immediate_children
            current = set([child[0] for child in immediate_children])

        return children_by_depth

    def immediate_children(self, site_id, by=None):
        start_node = self.__graph__[site_id]

        if by:
            return start_node[by]

        children = []
        for related_children in start_node.values():
            children += related_children

        return children

    def normalize_all_relationships(self, parent):
        parent_id = parent.id if isinstance(parent, SeoSite) else parent
        children_by_depth = self.children_by_depth(parent_id, depth=10)

        normalized = []
        for depth, children in children_by_depth.iteritems():
            for child_id, weight, by_id in children:
                normalized.append(DenormalizedSiteRelationship(
                    parent_id=parent_id,
                    child_id=child_id,
                    weight=weight,
                    by_id=by_id,
                    depth=depth,
                ))
        DenormalizedSiteRelationship.objects.bulk_create(normalized)
