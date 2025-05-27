from django import forms
from .models import MQTTConfig

class MQTTConfigForm(forms.ModelForm):
    class Meta:
        model = MQTTConfig
        fields = ['broker_address', 'broker_port', 'set_topic', 'state_topic']
