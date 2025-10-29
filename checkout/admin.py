from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("name", "quantity", "price", "total_price")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "plan", "order_type", "status",
        "total_amount", "created_at"
    )
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "plan__title")
    inlines = [OrderItemInline]
    readonly_fields = ("created_at", "updated_at")
    actions = ["mark_as_paid", "mark_as_cancelled"]

    fieldsets = (
        ("Order Info", {
            "fields": ("user", "plan", "status", "total_amount")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    #  Custom tag showing order type
    def order_type(self, obj):
        """Displays whether order includes a plan, products, or both."""
        has_plan = bool(obj.plan)
        has_products = obj.items.filter(product__isnull=False).exists()
        if has_plan and has_products:
            return "Mixed (Plan + Products)"
        elif has_plan:
            return "Plan Only"
        elif has_products:
            return "Products Only"
        return "Empty"
    order_type.short_description = "Order Type"
    order_type.admin_order_field = "plan"

    #  Admin actions
    @admin.action(description="Mark selected orders as Paid")
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status="paid")
        self.message_user(request, f"{updated} order(s) marked as Paid.")

    @admin.action(description="Mark selected orders as Cancelled")
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status="cancelled")
        self.message_user(request, f"{updated} order(s) marked as Cancelled.")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "name", "quantity", "price", "total_price")
    search_fields = ("order__id", "name")
