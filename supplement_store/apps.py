from django.apps import AppConfig

class SupplementStoreConfig(AppConfig):
    name = 'supplement_store'

    def ready(self):
        import supplement_store.signals