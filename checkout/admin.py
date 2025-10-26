from django.contrib import admin
from .models import Order, OrderItem
# Register your models here.


class OrderItemInline(admin.TabularInline):
    """Display order items inside the Order admin page."""
    model = OrderItem
    extra = 0
    readonly_fields = ('name', 'quantity', 'price', 'total_price')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Orders."""
    list_display = (
        'id',
        'user',
        'plan',
        'total_amount',
        'status',
        'created_at',
        'updated_at',
    )
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__username', 'plan__title', 'id')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'plan', 'total_amount', 'created_at', 'updated_at')
    inlines = [OrderItemInline]

    fieldsets = (
        ("Order Details", {
            "fields": ("user", "plan", "total_amount", "status")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Separate view for individual order items (optional)."""
    list_display = ('id', 'order', 'name', 'quantity', 'price', 'total_price')
    search_fields = ('order__id', 'name')
    list_filter = ('order__status',)
    readonly_fields = ('order', 'name', 'quantity', 'price', 'total_price')
