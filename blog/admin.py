from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .forms import PostAdminForm
from .models import Post, PostTag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ("title", "author", "slug", "created", "modified")
    list_filter = ("author", "tags", "created", "modified")
    search_fields = ("title", "content")
    filter_horizontal = ("tags",)
    date_hierarchy = "created"
    autocomplete_fields = ("author", "tags")

    readonly_fields = ("preview_html",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "author",
                    "title",
                    "content",
                    "preview_html",
                    "file",
                    "tags",
                )
            },
        ),
    )

    def preview_html(self, obj):
        html = obj.content.html or "<em>{}</em>".format(_("(no content yet)"))
        return mark_safe(html)

    preview_html.short_description = _("rendered HTML")


@admin.register(PostTag)
class PostTagAdmin(admin.ModelAdmin):
    list_display = ("tag_name", "name")
    search_fields = ("tag_name", "name")
    ordering = ("tag_name",)
