from django.db import models
from django.conf import settings
from products.models import Product


class Subscription(models.Model):
    """Optional fitness or nutrition subscription plans."""
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Cart(models.Model):
    """
    Cart can belong to a user or to a guest (via session ID).
    If user is None, it's a session-based temporary cart.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        if self.user:
            return f"Cart (User: {self.user.username})"
        return f"Guest Cart ({self.id})"

    def total_price(self):
        total = sum(item.total_price() for item in self.items.all())
        if self.subscription:
            total += self.subscription.price
        return total

    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """A product inside a user's or guest's cart."""
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    def total_price(self):
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        """Auto-update item price from product if needed."""
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)
