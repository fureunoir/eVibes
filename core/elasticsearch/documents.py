from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from core.elasticsearch import COMMON_ANALYSIS, ActiveOnlyMixin, _add_multilang_fields
from core.models import Brand, Category, Product


class _BaseDoc(ActiveOnlyMixin, Document):
    name = fields.TextField(
        analyzer="standard",
        fields={
            "raw":       fields.KeywordField(ignore_above=256),
            "ngram":     fields.TextField(analyzer="name_ngram",
                                          search_analyzer="query_lc"),
            "phonetic":  fields.TextField(analyzer="name_phonetic"),
            "auto":      fields.TextField(
                             analyzer="autocomplete",
                             search_analyzer="autocomplete_search",
                         ),
        },
        attr=None,
    )

    description = fields.TextField(
        analyzer="standard",
        fields={
            "raw":       fields.KeywordField(ignore_above=256),
            "ngram":     fields.TextField(analyzer="name_ngram",
                                          search_analyzer="query_lc"),
            "phonetic":  fields.TextField(analyzer="name_phonetic"),
            "auto":      fields.TextField(
                             analyzer="autocomplete",
                             search_analyzer="autocomplete_search",
                         ),
        },
        attr=None,
    )

    class Index:
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": COMMON_ANALYSIS,
            "index": {
                "max_ngram_diff": 20,
            },
        }


class ProductDocument(_BaseDoc):
    rating = fields.FloatField(attr="rating")

    class Index(_BaseDoc.Index):
        name = "products"

    class Django:
        model = Product
        fields = ["uuid"]


_add_multilang_fields(ProductDocument)
registry.register_document(ProductDocument)


class CategoryDocument(_BaseDoc):
    class Index(_BaseDoc.Index):
        name = "categories"

    class Django:
        model = Category
        fields = ["uuid"]


_add_multilang_fields(CategoryDocument)
registry.register_document(CategoryDocument)


class BrandDocument(ActiveOnlyMixin, Document):
    name = fields.TextField(
        attr="name",
        analyzer="standard",
        fields={
            "raw": fields.KeywordField(ignore_above=256),
            "ngram": fields.TextField(
                analyzer="name_ngram", search_analyzer="query_lc"
            ),
            "phonetic": fields.TextField(analyzer="name_phonetic"),
        },
    )

    class Index:
        name = "brands"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": COMMON_ANALYSIS,
            "index": {"max_ngram_diff": 18},
        }

    class Django:
        model = Brand
        fields = ["uuid"]


registry.register_document(BrandDocument)
