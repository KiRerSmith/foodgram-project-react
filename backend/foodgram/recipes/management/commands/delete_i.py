import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Delete dara from database'

    """def add_arguments(self, parser):
        parser.add_argument('--path', type=str)"""

    def handle(self, *args, **kwargs):
        Ingredient.objects.all().delete()
