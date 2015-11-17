from django.core.management.base import BaseCommand
import csv
from seo.models import BusinessUnit

class Command(BaseCommand):
    args = "'/path/to/file.csv' (as string)"
    help = """
           Given the path to a CSV file in the format of 'buid, fc(0|1),
           Company Name' update the federal_contractor attributes
           on the Company model.
           """

    def handle(self, *args, **options):
        for arg in args:
            buids = [(line[0], line[1]) for line in csv.reader(open(arg, 'r'))]

            # Start at index 1 to exclude the header
            for buid in buids[1:]:
                try:
                    bu = BusinessUnit.objects.get(id=int(buid[0]))
                    bu.federal_contractor = buid[1] == "1"
                    bu.save()
                except bu.DoesNotExist:
                    print "Business Unit {0} does not exist.".format(buid)
