from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('process/', views.checkout_process, name='checkout_process'),
    path('<int:plan_id>/', views.checkout_plan, name='checkout_plan'),
]
