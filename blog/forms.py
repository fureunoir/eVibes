from django import forms

from blog.models import Post
from blog.widgets import MarkdownEditorWidget


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("author", "content", "tags", "title")
        widgets = {
            "content": MarkdownEditorWidget(attrs={"style": "min-height: 500px;"}),
        }
