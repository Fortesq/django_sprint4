from django.urls import include, path

from . import views

app_name = 'blog'

post_urls = [
    path('<int:post_id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    path(
        '<int:post_id>/delete/',
        views.PostDeleteView.as_view(), name='delete_post'),
    path(
        '<int:post_id>/edit/',
        views.PostUpdateView.as_view(), name='edit_post'),
    path(
        '<int:post_id>/comment/',
        views.CommentCreateView.as_view(), name='add_comment'),
    path(
        '<int:post_id>/edit_comment/<int:comment_id>/',
        views.CommentUpdateView.as_view(), name='edit_comment'),
    path(
        '<int:post_id>/delete_comment/<int:comment_id>/',
        views.CommentDeleteView.as_view(), name='delete_comment'),
]

urlpatterns = [
    path('', views.PostsListView.as_view(), name='index'),
    path('login_only/', views.simple_view),
    path('posts/', include(post_urls)),
    path(
        'category/<slug:category_slug>/',
        views.CategoryPosts.as_view(), name='category_posts'),
    path(
        'profile/<str:username>/',
        views.ProfileListView.as_view(), name='profile'),
    path(
        'edit_profile/<str:username>/',
        views.ProfileUpdateView.as_view(), name='edit_profile'),
]
