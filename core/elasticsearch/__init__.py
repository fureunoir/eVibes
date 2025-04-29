from django.conf import settings
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from django_elasticsearch_dsl import fields
from elasticsearch import NotFoundError
from elasticsearch.dsl import Q, Search

SMART_FIELDS = [
    "name^4",
    "name.ngram^3",
    "name.phonetic",
    "description^2",
    "description.ngram",
    "description.phonetic",
    "name.auto^4",
    "description.auto^2",
    "brand__name^2",
    "brand__name.ngram",
    "brand__name.auto",
    "category__name^2",
    "category__name.ngram",
    "category__name.auto",
    "title^4",
    "title.ngram^3",
    "title.phonetic",
    "title.auto^4",
]


def process_query(query: str = ""):
    """
    Perform a lenient, typo‑tolerant, multi‑index search.

    * Full‑text with fuzziness for spelling mistakes
    * `bool_prefix` for edge‑ngram autocomplete / “icontains”
    """
    if not query:
        raise ValueError(_("no search term provided."))

    query = query.strip()
    try:
        q = Q(
            "bool",
            should=[
                Q(
                    "multi_match",
                    query=query,
                    fields=SMART_FIELDS,
                    fuzziness="AUTO",
                    operator="and",
                ),
                Q(
                    "multi_match",
                    query=query,
                    fields=[f.replace(".auto", ".auto") for f in SMART_FIELDS if ".auto" in f],
                    type="bool_prefix",
                ),
            ],
            minimum_should_match=1,
        )

        search = Search(index=["products", "categories", "brands", "posts"]).query(q).extra(size=100)

        response = search.execute()

        results = {"products": [], "categories": [], "brands": []}
        for hit in response.hits:
            obj_uuid = getattr(hit, "uuid", hit.meta.id)
            obj_name = getattr(hit, "name", "N/A")
            if hit.meta.index == "products":
                results["products"].append({"uuid": obj_uuid, "name": obj_name})
            elif hit.meta.index == "categories":
                results["categories"].append({"uuid": obj_uuid, "name": obj_name})
            elif hit.meta.index == "brands":
                results["brands"].append({"uuid": obj_uuid, "name": obj_name})

        return results
    except NotFoundError:
        raise Http404


LANGUAGE_ANALYZER_MAP = {
    "ar": "arabic",
    "cs": "czech",
    "da": "danish",
    "de": "german",
    "en": "english",
    "es": "spanish",
    "fr": "french",
    "hi": "hindi",
    "it": "italian",
    "ja": "standard",  # Kuromoji plugin recommended for production
    "kk": "standard",  # No built‑in Kazakh stemmer ‑ falls back to ICU/standard
    "nl": "dutch",
    "pl": "standard",  # No built‑in Polish stemmer ‑ falls back to ICU/standard
    "pt": "portuguese",
    "ro": "romanian",
    "ru": "russian",
    "zh": "standard",  # smartcn / ICU plugin recommended for production
}


def _lang_analyzer(lang_code: str) -> str:
    """Return the best‑guess ES analyzer for an ISO language code."""
    base = lang_code.split("-")[0].lower()
    return LANGUAGE_ANALYZER_MAP.get(base, "standard")


class ActiveOnlyMixin:
    """QuerySet & indexing helpers, so only *active* objects are indexed."""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

    def should_index_object(self, obj):
        return getattr(obj, "is_active", False)


COMMON_ANALYSIS = {
    "filter": {
        "edge_ngram_filter": {
            "type": "edge_ngram",
            "min_gram": 1,
            "max_gram": 20,
        },
        "ngram_filter": {
            "type": "ngram",
            "min_gram": 2,
            "max_gram": 20,
        },
        "double_metaphone": {
            "type": "phonetic",
            "encoder": "double_metaphone",
            "replace": False,
        },
    },
    "analyzer": {
        "autocomplete": {
            "tokenizer": "standard",
            "filter": ["lowercase", "asciifolding", "edge_ngram_filter"],
        },
        "autocomplete_search": {
            "tokenizer": "standard",
            "filter": ["lowercase", "asciifolding"],
        },
        "name_ngram": {
            "tokenizer": "standard",
            "filter": ["lowercase", "asciifolding", "ngram_filter"],
        },
        "name_phonetic": {
            "tokenizer": "standard",
            "filter": ["lowercase", "asciifolding", "double_metaphone"],
        },
        "query_lc": {
            "tokenizer": "standard",
            "filter": ["lowercase", "asciifolding"],
        },
    },
}


def _add_multilang_fields(cls):
    for code, _lang in settings.LANGUAGES:
        lc = code.replace("-", "_").lower()
        analyzer = _lang_analyzer(code)

        setattr(
            cls,
            f"name_{lc}",
            fields.TextField(
                attr=f"name_{lc}",
                analyzer=analyzer,
                copy_to="name",
                fields={
                    "raw": fields.KeywordField(ignore_above=256),
                    "ngram": fields.TextField(analyzer="name_ngram", search_analyzer="query_lc"),
                    "phonetic": fields.TextField(analyzer="name_phonetic"),
                },
            ),
        )
        setattr(
            cls,
            f"description_{lc}",
            fields.TextField(
                attr=f"description_{lc}",
                analyzer=analyzer,
                copy_to="description",
                fields={
                    "raw": fields.KeywordField(ignore_above=256),
                    "ngram": fields.TextField(analyzer="name_ngram", search_analyzer="query_lc"),
                    "phonetic": fields.TextField(analyzer="name_phonetic"),
                },
            ),
        )
