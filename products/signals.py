from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import Review, Product


@receiver([post_save, post_delete], sender=Review)
def update_product_rating(sender, instance, **kwargs):
    """
    Automatically update a product's average rating whenever
    a review is added, updated, or deleted.
    """
    product = instance.product
    avg_rating = product.reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    product.rating = avg_rating
    product.save(update_fields=['rating'])
