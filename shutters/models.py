from django.db import models

class MQTTConfig(models.Model):
    broker_address = models.CharField(max_length=255, default="localhost")
    broker_port = models.IntegerField(default=1883)
    set_topic = models.CharField(max_length=255)
    state_topic = models.CharField(max_length=255)

    def __str__(self):
        return f"MQTT Config to {self.broker_address}:{self.broker_port}"

class Shutter(models.Model):
    STATES = [
            ('open', 'Open'),
            ('closed', 'Closed'),
            ('inprogress', 'In progress'),
            ('unknown', 'Unknown'),
        ]

    current_state = models.CharField(
            max_length=12,
            choices=STATES,
            default='unknown'
        )

    name = models.CharField(max_length=100)
    relay_open = models.IntegerField(default=1)
    relay_close = models.IntegerField(default=2)
    input_open = models.IntegerField(null=True, blank=True)
    input_close = models.IntegerField(null=True, blank=True)
    open_duration = models.FloatField(default=30.0)
    close_duration = models.FloatField(default=30.0)


    def __str__(self):
        return self.name
