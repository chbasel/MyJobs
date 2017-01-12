from haystack import indexes

from relationships.models import NormalizedSiteRelationship


class NormalizedSiteRelationshipIndex(indexes.SearchIndex, indexes.Indexable):
    id = indexes.IntegerField()
    parent = indexes.IntegerField()
    child = indexes.IntegerField()
    by = indexes.IntegerField()
    weight = indexes.FloatField()
    depth = indexes.IntegerField()
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return NormalizedSiteRelationship
