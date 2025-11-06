from django.contrib import admin
from .models import Cart, CartItem, Subscription

# Register your models here.


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subscription', 'total_price', 'created_at')
    inlines = [CartItemInline]

admin.site.register(Subscription)
