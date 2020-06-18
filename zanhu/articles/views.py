from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from articles.forms import ArticleForm
from zanhu.articles.models import Article
from zanhu.helpers import AuthorRequiredMixin


class ArticlesListView(LoginRequiredMixin, ListView):
    model = Article
    paginate_by = 20
    context_object_name = 'articles'
    template_name = 'articles/article_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ArticlesListView, self).get_context_data(*args, **kwargs)
        context['popular_tags'] = Article.objects.get_counted_tags()
        return context

    def get_queryset(self, **kwargs):
        return Article.objects.get_published()


class DraftsListView(ArticlesListView):
    """draft article list"""

    def get_queryset(self, **kwargs):
        return Article.objects.filter(user=self.request.user).get_drafts()


class CreateArticleView(LoginRequiredMixin, CreateView):
    """create article"""
    model = Article
    message = "您的文章已创建成功！"  # Django message scheme
    form_class = ArticleForm
    template_name = 'articles/article_create.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(CreateArticleView, self).form_valid(form)

    def get_success_url(self):
        """redirect after successful creation"""
        messages.success(self.request, self.message)  # message is passed to next request
        return reverse_lazy('articles:list')


class DetailArticleView(LoginRequiredMixin, DetailView):
    """article detail"""
    model = Article
    template_name = 'articles/article_detail.html'

    def get_queryset(self):
        return Article.objects.select_related('user').filter(slug=self.kwargs['slug'])


class EditArticleView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    """edit article"""
    model = Article
    message = "您的文章编辑成功！"
    form_class = ArticleForm
    template_name = 'articles/article_update.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(EditArticleView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse_lazy('articles:list')
