from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from six import python_2_unicode_compatible
from slugify import slugify
from taggit.managers import TaggableManager


@python_2_unicode_compatible
class ArticleQuerySet(models.query.QuerySet):
    """Customized QuerySet which improves the usability of model class"""
    def get_published(self):
        """return published article"""
        return self.filter(status="P")

    def get_drafts(self):
        """return drafts"""
        return self.filter(status="D")

    def get_counted_tags(self):
        tag_dict = {}
        query = self.get_published().annotate(tagged=models.Count('tags')).filter(tags__gt=0)
        for obj in query:
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else:
                    tag_dict[tag] += 1
        return tag_dict.items()


@python_2_unicode_compatible
class Article(models.Model):
    STATUS = (("D", "Draft"), ("P", "Published"))

    title = models.CharField(max_length=255, null=False, unique=True, verbose_name='标题')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="author", on_delete=models.SET_NULL, verbose_name='作者')
    image = models.ImageField(upload_to='articles_pictures/%Y/%m/%d/', verbose_name='文章图片')
    slug = models.SlugField(max_length=80, null=True, blank=True, verbose_name='(URL)别名')
    status = models.CharField(max_length=1, choices=STATUS, default='D', verbose_name='状态')  # 默认存入草稿箱
    content = MarkdownxField(verbose_name='内容', null=True, blank=True)
    edited = models.BooleanField(default=False, verbose_name='是否可编辑')
    tags = TaggableManager(help_text='多个标签使用,(英文)隔开', verbose_name='标签')
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    objects = ArticleQuerySet.as_manager()


    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        ordering = ("created_at",)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Article, self).save(*args, **kwargs)

    def get_markdown(self):
        """transform markdown text into html"""
        return markdownify(self.content)
