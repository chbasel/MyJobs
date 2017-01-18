from relationships import utils
from relationships.models import SiteRelationship
from relationships.tests.base import RelationshipsBaseTest


class GraphTest(RelationshipsBaseTest):
    def test_build_simple(self):
        """
        A simple graph should build from the SiteRelationship model.

        """
        graph = utils.Graph()
        self.assertEqual(graph.__graph__, {})

        parent = self.sites[0]
        child = self.sites[1]
        relationship = SiteRelationship.objects.create(
            parent=parent, child=child, by=self.by
        )

        expected = {
            relationship.parent.id: {
                relationship.by.id: [
                    (relationship.child.id, relationship.weight, self.by.id)
                ],
            },
        }
        graph = utils.Graph()
        self.assertDictEqual(graph.__graph__, expected)

    def test_build_complex(self):
        """
        A more complex graph should build correctly from the SiteRelationship
        model.

        """
        weight = 1
        site_relationships = [
            (self.sites[0], self.sites[1]),
            (self.sites[1], self.sites[2]),
            (self.sites[0], self.sites[3]),
            (self.sites[4], self.sites[5]),
        ]

        for parent, child in site_relationships:
            SiteRelationship.objects.create(
                parent=parent, child=child, by=self.by, weight=weight
            )

        expected = {
            self.sites[0].id: {
                self.by.id: [
                    (self.sites[1].id, weight, self.by.id),
                    (self.sites[3].id, weight, self.by.id),
                ],
            },
            self.sites[1].id: {
                self.by.id: [
                    (self.sites[2].id, weight, self.by.id),
                ],
            },
            self.sites[4].id: {
                self.by.id: [
                    (self.sites[5].id, weight, self.by.id),
                ],
            },
        }
        graph = utils.Graph()
        self.assertDictEqual(graph.__graph__, expected)

    def test_children_by_depth(self):
        weight = 1
        site_relationships = [
            (self.sites[0], self.sites[1]),
            (self.sites[1], self.sites[2]),
            (self.sites[0], self.sites[3]),
            (self.sites[4], self.sites[5]),
        ]

        for parent, child in site_relationships:
            SiteRelationship.objects.create(
                parent=parent, child=child, by=self.by, weight=weight
            )

        # Check results for only the first depth (default for depth).
        graph = utils.Graph()
        children = graph.children_by_depth(self.sites[0].id)
        expected = {
            1: [
                (self.sites[1].id, weight, self.by.id),
                (self.sites[3].id, weight, self.by.id),
            ],
        }
        self.assertDictEqual(children, expected)

        # Check results for first and second depth.
        expected[2] = [(self.sites[2].id, weight, self.by.id)]
        children = graph.children_by_depth(self.sites[0].id, depth=2)
        self.assertDictEqual(children, expected)

    def test_immediate_children(self):
        """
        Graph.immediate_children() should only get the immediate children
        for the provided site, even if there are more sub-children.

        """
        weight = 1
        site_relationships = [
            (self.sites[0], self.sites[1]),
            (self.sites[1], self.sites[2]),
        ]

        for parent, child in site_relationships:
            SiteRelationship.objects.create(
                parent=parent, child=child, by=self.by, weight=weight
            )

        graph = utils.Graph()
        immediate_children = graph.immediate_children(self.sites[0].id)
        expected = [(self.sites[1].id, weight, self.by.id)]
        self.assertItemsEqual(immediate_children, expected)
