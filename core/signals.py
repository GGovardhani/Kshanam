from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile, StreakTracker, HealthTracker


@receiver(post_save, sender=User)
def create_user_related_objects(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
        StreakTracker.objects.get_or_create(user=instance)
        HealthTracker.objects.get_or_create(user=instance)