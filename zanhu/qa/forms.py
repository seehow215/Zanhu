from django import forms
from markdownx.fields import MarkdownxFormField

from zanhu.qa.models import Question


class QuestionForm(forms.ModelForm):
    status = forms.CharField(widget=forms.HiddenInput())  # hidden
    content = MarkdownxFormField()

    class Meta:
        model = Question
        fields = ["title", "content", "tags", "status"]
