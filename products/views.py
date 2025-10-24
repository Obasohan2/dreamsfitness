from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages 
from django.db.models import Q
from .models import Product, Category, Review
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required


def all_products(request):
    """
    Display all available products with sorting, category filtering, and search.
    """
    products = Product.objects.filter(is_available=True)
    query = None
    category = None
    sort = None
    direction = None

    # --- Sorting ---
    if 'sort' in request.GET:
        sortkey = request.GET['sort']
        sort = sortkey

        sort_mapping = {
            'price': 'price',
            'rating': 'rating',
            'category': 'category__name',
            'name': 'name'
        }
        sortkey = sort_mapping.get(sortkey, 'name')

        if request.GET.get('direction') == 'desc':
            direction = 'desc'
            sortkey = f'-{sortkey}'
        else:
            direction = 'asc'

        products = products.order_by(sortkey)

    # --- Category Filtering ---
    if 'category' in request.GET:
        category_slug = request.GET['category']
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # --- Search ---
    if 'q' in request.GET:
        query = request.GET['q'].strip()
        if query:
            products = products.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )

    current_sorting = f'{sort}_{direction}' if sort else 'None'

    context = {
        'products': products,
        'search_term': query,
        'current_category': category,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def category_products(request, slug):
    """
    Display products in a specific category (only available ones).
    """
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_available=True)

    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'products/category_products.html', context)


def product_detail(request, slug):
    """
    Display single product details and related products.
    """
    product = get_object_or_404(Product, slug=slug, is_available=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)


@login_required
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            #  Add success message
            messages.success(request, "Your review has been submitted successfully!")
            return redirect('products:product_detail', slug=slug)
        else:
            # Optional: add error message if invalid form
            messages.error(request, "There was an error submitting your review. Please check the form.")
    else:
        form = ReviewForm()
      #  Add the review form to the product detail context
    return render(request, 'products/product_detail.html', {
        'product': product,
        'review_form': form,
        'reviews': product.reviews.all(),
    })