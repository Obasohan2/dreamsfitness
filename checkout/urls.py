from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('session/', views.checkout_session, name='checkout_session'),
    path('success/', views.checkout_success, name='checkout_success'),
    path('cancel/', views.checkout_cancel, name='checkout_cancel'),
]
