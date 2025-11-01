from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path(
        'change-password/',
        auth_views.PasswordChangeView.as_view(
            template_name='accounts/change_password.html',
            success_url=reverse_lazy('profile')
        ),
        name='change_password'
    ),
]

