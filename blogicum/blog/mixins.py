from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

from .forms import PostForm
from .models import Comment, Post


class PostMixin:
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=instance.pk)
        return super().dispatch(request, *args, **kwargs)


class CommentMixin:
    model = Comment
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            post__id=self.kwargs['post_id']
        )
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=instance.post_id)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={
                'post_id': self.kwargs[self.pk_url_kwarg]
            }
        )
