from django.shortcuts import render
from .models import Product, Category


def all_products(request):
    """Display all available products."""
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'products/products.html', context)