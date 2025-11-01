from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.feed, name='feed'),
    path('create/', views.create_post, name='create_post'),
    path('<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]
