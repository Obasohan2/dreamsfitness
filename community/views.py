from django.db.models import Exists, OuterRef, Value, BooleanField
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Post, Comment, Like
from .forms import PostForm, CommentForm
from django.contrib import messages
from django.urls import reverse


def feed(request):
    """Unregistered users can view posts but not interact."""
    posts = (
        Post.objects
        .select_related('author')
        .prefetch_related('comments', 'likes')
        .order_by('-created_at')
    )

    if request.user.is_authenticated:
        user_likes = Like.objects.filter(post=OuterRef('pk'), user=request.user)
        posts = posts.annotate(liked_by_user=Exists(user_likes))
    else:
        posts = posts.annotate(liked_by_user=Value(False, output_field=BooleanField()))

    comment_form = CommentForm() if request.user.is_authenticated else None

    return render(request, 'community/feed.html', {
        'posts': posts,
        'comment_form': comment_form,
    })


@login_required
def create_post(request):
    """Only registered users can create posts."""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('community:feed')
    else:
        form = PostForm()
    return render(request, 'community/create_post.html', {'form': form})


def toggle_like(request, post_id):
    """Only registered users can like/unlike posts."""
    if not request.user.is_authenticated:
        return JsonResponse({'redirect': '/accounts/login/?next=' + request.path}, status=401)

    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({'liked': liked, 'count': post.likes.count()})


def add_comment(request, post_id):
    """Only registered users can comment."""
    if not request.user.is_authenticated:
        return redirect('/accounts/login/?next=' + request.path)

    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    return redirect('community:feed')


@login_required
def delete_post(request, post_id):
    """Allow post author or admin to delete a post."""
    post = get_object_or_404(Post, id=post_id)

    if request.user == post.author or request.user.is_superuser:
        post.delete()
        messages.success(request, "Post deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this post.")

    return redirect('community:feed')


@login_required
def delete_comment(request, comment_id):
    """Allow comment author or admin to delete a comment."""
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user == comment.author or request.user.is_superuser:
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this comment.")

    return redirect('community:feed')
