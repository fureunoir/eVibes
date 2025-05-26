from django.db.models import CASCADE, CharField, FileField, ForeignKey, ManyToManyField
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from markdown.extensions.toc import TocExtension
from markdown_field import MarkdownField

from core.abstract import NiceModel


class Post(NiceModel):
    is_publicly_visible = True

    author = ForeignKey(to="vibes_auth.User", on_delete=CASCADE, blank=False, null=False, related_name="posts")
    title = CharField(
        unique=True, max_length=128, blank=False, null=False, help_text=_("post title"), verbose_name=_("title")
    )
    content = MarkdownField(
        "content",
        extensions=[
            TocExtension(toc_depth=3),
            "pymdownx.arithmatex",
            "pymdownx.b64",
            "pymdownx.betterem",
            "pymdownx.blocks.admonition",
            "pymdownx.blocks.caption",
            "pymdownx.blocks.definition",
            "pymdownx.blocks.details",
            "pymdownx.blocks.html",
            "pymdownx.blocks.tab",
            "pymdownx.caret",
            "pymdownx.critic",
            "pymdownx.emoji",
            "pymdownx.escapeall",
            "pymdownx.extra",
            "pymdownx.fancylists",
            "pymdownx.highlight",
            "pymdownx.inlinehilite",
            "pymdownx.keys",
            "pymdownx.magiclink",
            "pymdownx.mark",
            "pymdownx.pathconverter",
            "pymdownx.progressbar",
            "pymdownx.saneheaders",
            "pymdownx.smartsymbols",
            "pymdownx.snippets",
            "pymdownx.striphtml",
            "pymdownx.superfences",
            "pymdownx.tasklist",
            "pymdownx.tilde",
        ],
        blank=True,
        null=True,
    )
    file = FileField(upload_to="posts/", blank=True, null=True)
    slug = AutoSlugField(populate_from="title", allow_unicode=True, unique=True, editable=False)
    tags = ManyToManyField(to="blog.PostTag", blank=True, related_name="posts")

    def __str__(self):
        return f"{self.title} | {self.author.first_name} {self.author.last_name}"

    class Meta:
        verbose_name = _("post")
        verbose_name_plural = _("posts")

    def save(self, **kwargs):
        if not any([self.file, self.content]) or all([self.file, self.content]):
            raise ValueError(_("a markdown file or markdown content must be provided - mutually exclusive"))
        super().save(**kwargs)


class PostTag(NiceModel):
    is_publicly_visible = True

    tag_name = CharField(
        blank=False,
        null=False,
        max_length=255,
        help_text=_("internal tag identifier for the post tag"),
        verbose_name=_("tag name"),
    )
    name = CharField(
        max_length=255,
        help_text=_("user-friendly name for the post tag"),
        verbose_name=_("tag display name"),
        unique=True,
    )

    def __str__(self):
        return self.tag_name

    class Meta:
        verbose_name = _("post tag")
        verbose_name_plural = _("post tags")
