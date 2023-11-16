from django.db.models import Count
from django.utils import timezone

from .models import Post


def get_posts_queryset(
        manager=Post.objects,
        apply_select_related=True,
        apply_filters=False,
        apply_annotation=False
):
    queryset = manager.select_related('author', 'location', 'category')
    if apply_filters:
        queryset = queryset.filter(
            is_published=True,
            pub_date__lt=timezone.now(),
            category__is_published=True
        )
    if apply_annotation:
        queryset = queryset.annotate(comment_count=Count('comments'))
    return queryset.order_by('-pub_date')
