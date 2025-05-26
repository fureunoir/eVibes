from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from blog.models import Post
from core.elasticsearch import COMMON_ANALYSIS, ActiveOnlyMixin


class PostDocument(ActiveOnlyMixin, Document):
    title = fields.TextField(
        attr="title",
        analyzer="standard",
        fields={
            "raw": fields.KeywordField(ignore_above=256),
            "ngram": fields.TextField(analyzer="name_ngram", search_analyzer="query_lc"),
            "phonetic": fields.TextField(analyzer="name_phonetic"),
        },
    )

    class Index:
        name = "posts"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": COMMON_ANALYSIS,
            "index": {"max_ngram_diff": 18},
        }

    class Django:
        model = Post
        fields = ["uuid"]

    def prepare_title(self, instance):
        return getattr(instance, "title", "") or ""


registry.register_document(PostDocument)
