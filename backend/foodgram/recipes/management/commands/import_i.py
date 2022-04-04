import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load dara from csv file into the database'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **kwargs):
        path = kwargs['path']
        with open(path, mode='rt', encoding='cp1251') as f:
            reader = csv.reader(f)
            for row in reader:
                Ingredient.objects.create(
                    name=row[0],
                    measurement_unit=row[1],
                )
