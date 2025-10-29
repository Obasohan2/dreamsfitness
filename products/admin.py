from django.contrib import admin
from django.utils.html import mark_safe
from .models import Product, Category


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'price',
        'rating',
        'is_available',
        'is_digital',
        'image_preview',
    )
    list_filter = ('category', 'is_available', 'is_digital')
    search_fields = ('name', 'category__name')
    ordering = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.images:
            return mark_safe(f'<img src="{obj.images.url}" width="60" height="60" style="border-radius:5px;object-fit:cover;" />')
        return "-"
    image_preview.short_description = "Image"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = "Number of Products"
