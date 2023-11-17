from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm, ProfileForm
from .mixins import CommentMixin, PostMixin
from .models import Category, Comment, Post
from .utils import get_posts_queryset


class PostsListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = settings.PAGINATE_ON_PAGE
    ordering = '-pub_date'

    def get_queryset(self):
        return get_posts_queryset(
            manager=Post.objects,
            apply_filters=True,
            apply_annotation=True
        )


class PostDetailView(DetailView):
    queryset = get_posts_queryset()
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        instance = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if (
                self.request.user != instance.author
                and not (
                instance.is_published
                and instance.category.is_published
                and instance.pub_date <= timezone.now())
        ):
            raise Http404('Страница не существует')
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
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CategoryPosts(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/category.html'
    slug_url_kwarg = 'category_slug'
    category = None
    paginate_by = settings.PAGINATE_ON_PAGE

    def get_object(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'], is_published=True)
        return self.category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

    def get_queryset(self):
        category = self.get_object()

        queryset = get_posts_queryset(
            manager=category.posts,
            apply_filters=True,
            apply_annotation=True
        )
        return queryset


class PostUpdateView(LoginRequiredMixin, PostMixin, UpdateView):

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs[self.pk_url_kwarg]}
        )


class PostDeleteView(LoginRequiredMixin, PostMixin, DeleteView):
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['form'].instance = self.get_object()
        return context

    def dispatch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=instance.pk)
        return super().dispatch(request, *args, **kwargs)


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateView(CommentMixin, UpdateView):
    form_class = CommentForm
    template_name = 'blog/create.html'


class CommentDeleteView(CommentMixin, DeleteView):
    template_name = 'blog/comment.html'


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = settings.PAGINATE_ON_PAGE
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_user(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        user = self.get_user()
        if self.request.user == user:
            queryset = get_posts_queryset(
                manager=user.posts,
                apply_filters=False,
                apply_annotation=True
            )
        else:
            queryset = get_posts_queryset(
                manager=user.posts,
                apply_filters=True,
                apply_annotation=True
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_user()
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
