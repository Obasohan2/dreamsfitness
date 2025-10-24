from django.urls import path
from . import views


urlpatterns = [
    path('pricing/', views.pricing_view, name='pricing'),
    path('checkout/<int:plan_id>/', views.checkout, name='checkout'),
    path('checkout-session/<int:plan_id>/', views.checkout_session, name='checkout_session'),
]
