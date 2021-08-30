from django.contrib import admin
from .models import Article, Comment

from django.contrib import admin
from mce_filebrowser.admin import MCEFilebrowserAdmin

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author")
    class Media:
        js = [
            #   'tiny_mce.js',  # nie ma ikon 
            #   'tiny_mce_popup.js',  # 1ok
            #   'tinymce_setup.js',  # 1ok
            #   'jquery.min.js',
            #   'jquery.tinymce.min.js',
            #   'tiny_mce.js',
            #   'tinymce.min.js',
            #   'tiny_mce_popup.js',
            #   'tiny_mce_src.js',
             ]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'body', 'post', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)
