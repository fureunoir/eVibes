from evibes.settings.base import *  # noqa: F403

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': ['http://elasticsearch:9200'],
        'basic_auth': ('elastic', getenv("ELASTIC_PASSWORD")),  # noqa: F405
        'verify_certs': False,
        'ssl_show_warn': False,
    },
}

ELASTICSEARCH_DSL_AUTOSYNC = True
ELASTICSEARCH_DSL_PARALLEL = False
ELASTICSEARCH_DSL_SIGNAL_PROCESSOR = (
    "django_elasticsearch_dsl.signals.CelerySignalProcessor"
)
