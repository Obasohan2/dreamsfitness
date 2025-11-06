from decimal import Decimal
from django.conf import settings
from products.models import Product
from subscriptions.models import SubPlan


class Cart:
    """Session-based shopping cart supporting both products and subscriptions."""

    def __init__(self, request):
        """
        Initialize the cart.
        Ensures the session always contains 'items' and 'subscription' keys.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)

        # Ensure cart structure exists and is consistent
        if not cart or 'items' not in cart or 'subscription' not in cart:
            cart = {
                'items': {},          # all products
                'subscription': None  # optional subscription plan
            }
            self.session[settings.CART_SESSION_ID] = cart

        self.cart = cart

    # ---------------------- PRODUCT METHODS ----------------------

    def add(self, product, quantity=1, override_quantity=False):
        """Add or update a product in the cart."""
        product_id = str(product.id)

        if 'items' not in self.cart:
            self.cart['items'] = {}

        if product_id not in self.cart['items']:
            self.cart['items'][product_id] = {
                'quantity': 0,
                'price': str(product.price),
            }

        if override_quantity:
            self.cart['items'][product_id]['quantity'] = quantity
        else:
            self.cart['items'][product_id]['quantity'] += quantity

        self.save()

    def remove(self, product):
        """Remove a product from the cart."""
        product_id = str(product.id)
        if 'items' in self.cart and product_id in self.cart['items']:
            del self.cart['items'][product_id]
            self.save()

    def clear_products(self):
        """Remove all products but keep subscription."""
        self.cart['items'] = {}
        self.save()

    # ---------------------- ITERATION ----------------------

    def __iter__(self):
        """Iterate over all products and optional subscription in the cart."""
        items = self.cart.get('items', {})
        product_ids = items.keys()
        products = Product.objects.filter(id__in=product_ids)

        # Attach Product objects to items
        for product in products:
            item = items[str(product.id)]
            item['product'] = product
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

        # Also yield subscription (if any)
        sub_data = self.cart.get('subscription')
        if sub_data:
            yield {
                'product': SubPlan(
                    id=sub_data['id'],
                    title=sub_data['title'],
                    price=Decimal(sub_data['price'])
                ),
                'quantity': 1,
                'price': Decimal(sub_data['price']),
                'total_price': Decimal(sub_data['price']),
                'is_subscription': True,
            }

    def __len__(self):
        """Return total quantity of products in the cart."""
        items = self.cart.get('items', {})
        return sum(item['quantity'] for item in items.values())

    # ---------------------- SUBSCRIPTION METHODS ----------------------

    def add_subscription(self, subplan):
        """Attach a subscription to the cart."""
        self.cart['subscription'] = {
            'id': subplan.id,
            'title': subplan.title,
            'price': str(subplan.price),
        }
        self.save()

    def remove_subscription(self):
        """Remove the current subscription from the cart."""
        self.cart['subscription'] = None
        self.save()

    def get_subscription(self):
        """Return the SubPlan object if selected."""
        sub_data = self.cart.get('subscription')
        if sub_data:
            try:
                return SubPlan.objects.get(id=sub_data['id'])
            except SubPlan.DoesNotExist:
                self.remove_subscription()
        return None

    # ---------------------- PRICE METHODS ----------------------

    def get_total_price(self):
        """Calculate total price for all products."""
        items = self.cart.get('items', {})
        return sum(Decimal(item['price']) * item['quantity'] for item in items.values())

    def get_total_with_subscription(self):
        """Calculate combined total (products + subscription)."""
        total = self.get_total_price()
        sub_data = self.cart.get('subscription')
        if sub_data:
            total += Decimal(sub_data['price'])
        return total

    # ---------------------- SESSION MANAGEMENT ----------------------

    def clear(self):
        """Completely clear cart (products + subscription)."""
        self.session[settings.CART_SESSION_ID] = {
            'items': {},
            'subscription': None,
        }
        self.save()

    def save(self):
        """Mark session as modified to ensure data is saved."""
        self.session.modified = True
