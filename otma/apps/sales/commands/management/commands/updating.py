from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from otma.apps.sales.commands.models import Group, Product
from otma.apps.sales.commands.service import CommunicationController
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)


class Command(BaseCommand):

    help = 'Check changes in menu.'

    def add_arguments(self, parser):
        self.filename = None
        self.extension = None
        self.model = None
        self.dependency_model = None
        parser.add_argument("-e", "--extension")
        parser.add_argument("-f", "--filename")

    def handle(self, *args, **options):
        django.setup()
        if options['extension']:
            self.extension = options['extension']
        if options['filename']:
            self.filename = options['filename']
            if self.filename == 'products':
                self.model = Product
                self.dependency_model = Group
            elif self.filename == 'groups':
                self.model = Group
        communication = CommunicationController()
        communication.field_search(model=self.model, filename=self.filename, extension=self.extension, dependency=self.dependency_model)
