# coding=utf-8
from django.contrib import admin
from . import models


class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'isbn', 'price', 'publisher', 'language')     # 限定显示的字段

    list_filter = ('language', 'price', 'publisher')
    search_fields = ('isbn', 'name', 'publisher')

# 评论管理
class CommentAdmin(admin.ModelAdmin):
    list_display = ('bid', 'aid', 'content', 'date')     # 限定显示的字段
    search_fields = ('bid', 'aid', 'content')
    list_filter = ('bid', 'date',)


admin.site.register(models.Book, BookAdmin)
admin.site.register(models.Account)
admin.site.register(models.Order)
admin.site.register(models.OrderBookRelation)
admin.site.register(models.ShopCart)
admin.site.register(models.Comment, CommentAdmin)
# Register your models here.


