from typing import Any
from django import http
from django.db import models
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.utils import timezone
from .forms import CommentForm, PostForm, ProfileForm
from django.views.generic import CreateView, DetailView, DeleteView, ListView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .models import Category, Comment, Post
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


POST_LIMIT = 5

def get_base_query():
    return Post.objects.select_related(
        'author', 'location', 'category'
    ).filter(
        is_published=True,
        pub_date__lt=timezone.now(),
        category__is_published=True
    )

@login_required
def simple_view(request):
    return HttpResponse('Страница для залогиненных пользователей!')





class PostsListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10
    ordering = '-pub_date'
    queryset = Post.objects.select_related(
        'category',
        'author',
        'location',
    ).filter(
        is_published=True,
        pub_date__lt=timezone.now(),
        category__is_published=True,
    ).annotate(comment_count=Count('comments'))




class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        instance = get_object_or_404(Post, pk=self.kwargs['post_id'], is_published=True)
        if instance.category and not instance.category.is_published:
            raise Http404("Категория не опубликована")

        return instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context
    




class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


    def form_valid(self, form):
        form.instance.author = self.request.user
        if form.instance.pub_date > timezone.now():
            form.instance.is_published = False
        else:
            form.instance.is_published = True
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username}) 


class CategoryPosts(ListView):
    model = Post
    template_name = 'blog/category.html'
    slug_url_kwarg = 'category_slug'
    category = None
    paginate_by = 10

    def get_queryset(self):
        # Получите объект категории или верните 404, если он не опубликован
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'], is_published=True)
        queryset = Post.objects.select_related(
            'category',
            'author',
            'location',
        ).filter(
            is_published=True,
            pub_date__lt=timezone.now(),
            category=self.category,
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context



class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = "post_id"
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("blog:post_detail", kwargs={"post_id": self.kwargs["post_id"]})

class PostDeleteView(DeleteView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = "post_id"
    template_name = 'blog/create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, pk=kwargs['post_id'])
        if post.author != self.request.user:
            if not (post.is_published
                    and post.category.is_published
                    and post.pub_date <= timezone.now()):
                raise Http404('Page does not exist')
        context['comments'] = post.post_comments.select_related(
            'author')
        context['form'] = CommentForm()
        return context



@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=pk) 


class CommentMixin:
    model = Comment

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id']
        )
        if instance.author != request.user:
            return HttpResponse()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={
                'post_id': self.kwargs['post_id']
            }
        )



class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    post_obj = None

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy("blog:post_detail", kwargs={"post_id": self.kwargs["post_id"]})



class CommentUpdateView(CommentMixin, UpdateView):
    form_class = CommentForm
    template_name = 'blog/create.html'
    slug_field = 'comment_id'
    pk_url_kwarg = 'comment_id'


class CommentDeleteView(CommentMixin, DeleteView):
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_object(self):
        return get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id']
        )

    

class ProfileListView(ListView): 
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_queryset(self):
        user = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return Post.objects.select_related(
            'category',
            'location',
            'author'
        ).filter(
            author=user
        ).order_by('-pub_date').annotate(comment_count=Count('comments'))
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username'],
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user
    
    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user}
        )



