import sys
from django.apps import AppConfig

class ShuttersConfig(AppConfig):
    name = 'shutters'

    def ready(self):
        if 'runserver' in sys.argv:
            from .mqtt_client import MQTTService
            MQTTService()
