from django import forms
from markdownx.fields import MarkdownxFormField

from zanhu.articles.models import Article


class ArticleForm(forms.ModelForm):
    status = forms.CharField(widget=forms.HiddenInput())  # hidden
    edited = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)  # hidden
    content = MarkdownxFormField()

    class Meta:
        model = Article
        fields = ["title", "content", "image", "tags", "status", "edited"]
