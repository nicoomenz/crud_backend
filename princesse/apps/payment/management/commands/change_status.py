from django.core.management.base import BaseCommand

from payment.handlers import handle_update_status

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        handle_update_status()