from django.db.models import Exists, OuterRef
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Post, Comment, Like
from .forms import PostForm, CommentForm


@login_required
def feed(request):
    user_likes = Like.objects.filter(post=OuterRef('pk'), user=request.user)
    posts = (
        Post.objects
        .select_related('author')
        .prefetch_related('comments', 'likes')
        .annotate(liked_by_user=Exists(user_likes))
        .order_by('-created_at')
    )
    comment_form = CommentForm()
    return render(request, 'community/feed.html', {
        'posts': posts,
        'comment_form': comment_form,
    })


@login_required
def create_post(request):
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


@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({'liked': liked, 'count': post.likes.count()})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('community:feed')
    return redirect('community:feed')
