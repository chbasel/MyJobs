from haystack import indexes

from relationships.models import NormalizedSiteRelationship


class NormalizedSiteRelationshipIndex(indexes.SearchIndex, indexes.Indexable):
    parent = indexes.IntegerField()
    child = indexes.IntegerField()
    by = indexes.IntegerField()
    weight = indexes.FloatField()
    depth = indexes.IntegerField()
    text = indexes.CharField(document=True)

    def get_model(self):
        return NormalizedSiteRelationship

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def prepare_parent(self, obj):
        return obj.parent.id

    def prepare_child(self, obj):
        return obj.child.id

    def prepare_by(self, obj):
        return obj.by.id
