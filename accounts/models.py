from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


def user_directory_path(instance, filename):
    return f'profile_pics/user_{instance.user.id}/{filename}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_directory_path, default='profile_pics/default-avatar.png')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


# Auto create/update profile
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    from django.core.exceptions import ObjectDoesNotExist
    if created:
        Profile.objects.create(user=instance)
    else:
        try:
            instance.profile.save()
        except ObjectDoesNotExist:
            Profile.objects.create(user=instance)
