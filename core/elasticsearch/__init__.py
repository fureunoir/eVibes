from django.conf import settings
from django.http import Http404
from django.utils.text import slugify
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
        # Build the boolean query
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
                    fields=[f for f in SMART_FIELDS if f.endswith('.auto')],
                    type="bool_prefix",
                ),
            ],
            minimum_should_match=1,
        )

        # Execute search across multiple indices
        search = Search(index=["products", "categories", "brands", "posts"]).query(q).extra(size=100)
        response = search.execute()

        # Collect results, guard against None values
        results = {"products": [], "categories": [], "brands": [], "posts": []}
        for hit in response.hits:
            obj_uuid = getattr(hit, "uuid", None) or hit.meta.id
            obj_name = getattr(hit, "name", None) or getattr(hit, "title", None) or "N/A"
            # Safely generate a slug
            obj_slug = getattr(hit, "slug", None) or slugify(obj_name)

            idx = hit.meta.index
            if idx in results:
                results[idx].append({
                    "uuid": str(obj_uuid),
                    "name": obj_name,
                    "slug": obj_slug,
                })
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
    "ja": "standard",
    "kk": "standard",
    "nl": "dutch",
    "pl": "standard",
    "pt": "portuguese",
    "ro": "romanian",
    "ru": "russian",
    "zh": "standard",
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
        "edge_ngram_filter": {"type": "edge_ngram", "min_gram": 1, "max_gram": 20},
        "ngram_filter": {"type": "ngram", "min_gram": 2, "max_gram": 20},
        "double_metaphone": {"type": "phonetic", "encoder": "double_metaphone", "replace": False},
    },
    "analyzer": {
        "autocomplete": {"tokenizer": "standard", "filter": ["lowercase", "asciifolding", "edge_ngram_filter"]},
        "autocomplete_search": {"tokenizer": "standard", "filter": ["lowercase", "asciifolding"]},
        "name_ngram": {"tokenizer": "standard", "filter": ["lowercase", "asciifolding", "ngram_filter"]},
        "name_phonetic": {"tokenizer": "standard", "filter": ["lowercase", "asciifolding", "double_metaphone"]},
        "query_lc": {"tokenizer": "standard", "filter": ["lowercase", "asciifolding"]},
    },
}


def _add_multilang_fields(cls):
    """
    Dynamically add multilingual name/description fields and prepare methods to guard against None.
    """
    for code, _lang in settings.LANGUAGES:
        lc = code.replace("-", "_").lower()
        # name_{lc}
        name_field = f"name_{lc}"
        setattr(
            cls,
            name_field,
            fields.TextField(
                attr=name_field,
                analyzer=_lang_analyzer(code),
                copy_to="name",
                fields={
                    "raw": fields.KeywordField(ignore_above=256),
                    "ngram": fields.TextField(analyzer="name_ngram", search_analyzer="query_lc"),
                    "phonetic": fields.TextField(analyzer="name_phonetic"),
                },
            ),
        )

        # prepare_name_{lc} to ensure no None values
        def make_prepare(attr):
            return lambda self, instance: getattr(instance, attr, "") or ""

        setattr(cls, f"prepare_{name_field}", make_prepare(name_field))

        # description_{lc}
        desc_field = f"description_{lc}"
        setattr(
            cls,
            desc_field,
            fields.TextField(
                attr=desc_field,
                analyzer=_lang_analyzer(code),
                copy_to="description",
                fields={
                    "raw": fields.KeywordField(ignore_above=256),
                    "ngram": fields.TextField(analyzer="name_ngram", search_analyzer="query_lc"),
                    "phonetic": fields.TextField(analyzer="name_phonetic"),
                },
            ),
        )
        setattr(cls, f"prepare_{desc_field}", make_prepare(desc_field))
