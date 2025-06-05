# from django.db.models.signals import post_save
# from django.contrib.auth.signals import user_logged_in, user_logged_out
# from django.dispatch import receiver
# from django.utils import timezone

# from rest_framework.authtoken.models import Token

# from user.models import User


# @receiver(post_save, sender=User)
# def create_auth_token(sender, instance=None, created=False, **kwargs):
#     Token.objects.get_or_create(user=instance)