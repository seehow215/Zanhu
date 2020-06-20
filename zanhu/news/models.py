from __future__ import unicode_literals
import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from six import python_2_unicode_compatible

from zanhu.notifications.views import notification_handler


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

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(News, self).save()
        if not self.reply:
            channel_layer = get_channel_layer()
            payload = {
                'type': 'receive',
                'key': 'additional_news',
                'actor_name': self.user.username,
            }
            async_to_sync(channel_layer.group_send)('notifications', payload)

    def switch_like(self, user):
        """点赞或取消赞"""
        if user in self.liked.all():  # 如果用户已经赞过，则取消赞
            self.liked.remove(user)
        else:  # 如果用户没有赞过，则添加赞
            self.liked.add(user)
            # 通知楼主
            notification_handler(user, self.user, 'L', self, id_value=str(self.uuid_id), key='social_update')

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
        # 通知楼主
        notification_handler(user, parent.user, 'R', parent, id_value=str(parent.uuid_id), key='social_update')

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
