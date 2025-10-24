from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.all_products, name='all_products'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
    path('<slug:slug>/add-review/', views.add_review, name='add_review'),
]
