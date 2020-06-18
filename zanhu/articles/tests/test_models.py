from test_plus.test import TestCase

from zanhu.articles.models import Article


class ArticlesModelsTest(TestCase):
    def setUp(self):
        """initialization"""
        self.user = self.make_user("test_user")
        self.other_user = self.make_user("other_test_user")
        self.article = Article.objects.create(
            title="第一篇文章",
            content="程序员梦工厂",
            status="P",
            user=self.user,
        )
        self.not_p_article = Article.objects.create(
            title="第二篇文章",
            content="""慕课网-程序员的梦工厂""",
            user=self.user,
        )

    def test_object_instance(self):
        """assert instance created is Article"""
        assert isinstance(self.article, Article)
        assert isinstance(self.not_p_article, Article)
        assert isinstance(Article.objects.get_published()[0], Article)

    def test_return_values(self):
        """check return values"""
        assert self.article.status == "P"
        assert self.article.status != "p"
        assert self.not_p_article.status == "D"
        assert str(self.article) == "第一篇文章"
        assert self.article in Article.objects.get_published()
        assert Article.objects.get_published()[0].title == "第一篇文章"
        assert self.not_p_article in Article.objects.get_drafts()
