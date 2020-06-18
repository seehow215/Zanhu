from __future__ import unicode_literals
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from six import python_2_unicode_compatible


@python_2_unicode_compatible
class News(models.Model):
    uuid_id =models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL,
                             related_name='publisher', verbose_name='用户')
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE,
                               related_name='thread', verbose_name='自关联')
    content = models.TextField(verbose_name='动态内容')
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_news', verbose_name='点赞用户')
    reply = models.BooleanField(default=False, verbose_name='是否为评论')
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '首页'
        verbose_name_plural = verbose_name
        ordering = ('-created_at',)

    def __str__(self):
        return self.content

    def switch_like(self, user):
        """like or dislike"""
        if user in self.liked.all():
            self.liked.remove(user)
        else:
            self.liked.add(user)

    def get_parent(self):
        if self.parent:
            return self.parent
        else:
            return self

    def reply_this(self, user, text):
        """
        reply to news
        :param user: user who are replying
        :param text: reply text
        :return:
        """
        parent = self.get_parent()
        News.objects.create(
            user=user,
            content=text,
            reply=True,
            parent=parent
        )

    def get_thread(self):
        """return all threads related to the current thread"""
        parent = self.get_parent()
        return parent.thread.all()

    def comment_count(self):
        return self.get_thread().count()

    def count_likers(self):
        return self.liked.count()

    def get_likers(self):
        return self.liked.all()
