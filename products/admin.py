from django.contrib import admin
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
        'image_preview',  # optional preview helper
    )
    list_filter = ('category', 'is_available', 'is_digital')
    search_fields = ('name', 'category__name')
    ordering = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def image_preview(self, obj):
        """
        Optional: Display a small image thumbnail in admin list view.
        """
        if obj.images:
            return f'<img src="{obj.images.url}" width="60" height="60" />'
        return "-"
    image_preview.allow_tags = True
    image_preview.short_description = "Image"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
