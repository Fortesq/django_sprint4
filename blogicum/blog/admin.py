from django.contrib import admin

from .models import Category, Comment, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published'
    )
    search_fields = ('title',)
    list_filter = ('is_published',)


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'author'
    )
    search_fields = ('author',)
    list_filter = ('is_published',)


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published'
    )
    search_fields = ('title',)
    list_filter = ('is_published',)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'is_published'
    )
    search_fields = ('title',)
    list_filter = ('is_published',)


admin.site.empty_value_display = 'Не задано'
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
