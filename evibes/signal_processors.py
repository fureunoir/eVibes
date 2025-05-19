from django.db import models
from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl.signals import CelerySignalProcessor


class SelectiveSignalProcessor(CelerySignalProcessor):
    def setup(self):
        for doc in registry.get_documents():
            model = doc.django.model
            models.signals.post_save.connect(self.handle_save, sender=model, weak=False)
            models.signals.post_delete.connect(self.handle_delete, sender=model, weak=False)
            models.signals.pre_delete.connect(self.handle_pre_delete, sender=model, weak=False)
            models.signals.m2m_changed.connect(self.handle_m2m_changed, sender=model, weak=False)

    def teardown(self):
        for doc in registry.get_documents():
            model = doc.django.model
            models.signals.post_save.disconnect(self.handle_save, sender=model)
            models.signals.post_delete.disconnect(self.handle_delete, sender=model)
            models.signals.pre_delete.disconnect(self.handle_pre_delete, sender=model)
            models.signals.m2m_changed.disconnect(self.handle_m2m_changed, sender=model)
