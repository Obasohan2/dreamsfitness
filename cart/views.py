from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from .cart import Cart

def cart_detail(request):
    """Display the cart contents."""
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {
        'cart_items': list(cart),
        'cart_count': len(cart),
        'total_price': cart.get_total_price(),
    })

def add_to_cart(request, product_id):
    """Add a product to the cart."""
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart = Cart(request)
    cart.add(product=product, quantity=quantity)
    return redirect('cart:cart_detail')

def update_cart(request, product_id):
    """Update product quantity in the cart."""
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart = Cart(request)
    cart.add(product=product, quantity=quantity, update_quantity=True)
    return redirect('cart:cart_detail')

def remove_from_cart(request, product_id):
    """Remove a product from the cart."""
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.remove(product)
    return redirect('cart:cart_detail')

def clear_cart(request):
    """Remove all items from the cart."""
    cart = Cart(request)
    cart.clear()
    return redirect('cart:cart_detail')
