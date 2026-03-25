from django.apps import AppConfig


class SchedulerConfig(AppConfig):
    name = 'events'
    def ready(self):
        import events.signals
