from princesse.apps.user.models import ClientPayer
from django.forms import ValidationError
import logging

logger = logging.getLogger(__name__)

def update_client(self, instance, client_data):
        try:
            client = ClientPayer.objects.get(id=client_data['id'])
            for key, value in client_data.items():
                if getattr(client, key) != value:
                    setattr(client, key, value)
            client.save()
            instance.client = client
            logger.info(f"Cliente modificado: {client}")
        except ClientPayer.DoesNotExist:
            raise ValidationError("El cliente con el ID proporcionado no existe")