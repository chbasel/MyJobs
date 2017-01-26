import logging
from collections import defaultdict

from relationships.models import SiteRelationship, DenormalizedSiteRelationship
from seo.models import SeoSite
from universal.helpers import make_chunks


logger = logging.getLogger(__name__)


class Graph(object):
    __graph__ = None

    def __init__(self):
        self.build()

    def build(self):
        """
        Creates a graph of all SiteRelationships and stores it
        in Graph.__graph__.

        Graph will be of the format:

        {
            parent_id: {
                relationship_id: [
                    (child_id, weight_of_relationship, relationship_id),
                    ...
                ],
                ...
            },
            ...
        }

        """
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
        """
        Gets all of the children for a site, arranged by depth.

        :param parent_id: The site id of the site children are wanted for.
        :param by: If provided, the relationship id of the relationship
                   the children should be related by.
        :param depth: The number of relationships that should be followed when
                      getting children.
        :return: A dictionary of children by depth, formatted:
                {depth: [(child_id, weight, relationship_id), ...], ...}

        """
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
        """
        Gets the immediate children (so only following one relationship) for
        a site.

        :param site_id: The site id of the site children are wanted for.
        :param by: If provided, the relationship id of the relationship
                   that the immediate children should be related by.
        :return: A list of children, formatted:
                    (child_id, weight, relationship_id)
        """
        start_node = self.__graph__[site_id]

        if by:
            return start_node[by]

        children = []
        for related_children in start_node.values():
            children += related_children

        return children

    def denormalize_all_relationships(self, parent):
        """
        Take the graph stored in __graph__ and flatten so that all relationships
        are accounted for, e.g. if a->b and b->c, then flatten to
        a->b, a->c, b->c.

        Stores flattened entries in the DenormalizedSiteRelationship table.

        :param parent: The site or site id that should be denormalized.

        """
        parent_id = parent.id if isinstance(parent, SeoSite) else parent
        children_by_depth = self.children_by_depth(parent_id, depth=10)

        denormalized = []
        for depth, children in children_by_depth.iteritems():
            for child_id, weight, by_id in children:
                denormalized.append(DenormalizedSiteRelationship(
                    parent_id=parent_id,
                    child_id=child_id,
                    weight=weight,
                    by_id=by_id,
                    depth=depth,
                ))

        for subset in make_chunks(denormalized):
            DenormalizedSiteRelationship.objects.bulk_create(subset)
