from django_filters import CharFilter, FilterSet, OrderingFilter, UUIDFilter

from blog.models import Post
from core.filters import CaseInsensitiveListFilter


class PostFilter(FilterSet):
    uuid = UUIDFilter(field_name="uuid", lookup_expr="exact")
    slug = CharFilter(field_name="slug", lookup_expr="exact")
    author = UUIDFilter(field_name="author__uuid", lookup_expr="exact")
    tags = CaseInsensitiveListFilter(field_name="tags__tag_name", label="Tags")

    order_by = OrderingFilter(
        fields=(
            ("uuid", "uuid"),
            ("slug", "slug"),
            ("author__uuid", "author"),
            ("created", "created"),
            ("modified", "modified"),
            ("?", "random"),
        )
    )

    class Meta:
        model = Post
        fields = ["uuid", "slug", "author", "tags", "order_by"]
