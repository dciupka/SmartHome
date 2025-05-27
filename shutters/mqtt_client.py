import json
import paho.mqtt.client as mqtt
from .models import MQTTConfig, Shutter
from .actions.shutter_actions import control_shutter

class MQTTService:
    def __init__(self):
        self.client = mqtt.Client()
        self.config = MQTTConfig.objects.first()
        self.pending = []
        if self.config:
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.connect(self.config.broker_address, self.config.broker_port)
            self.client.subscribe(self.config.state_topic)
            self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("MQTT connected")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
        except:
            return

        for shutter in Shutter.objects.all():
            shutter.refresh_from_db()
            key_o = f"input{shutter.input_open}"
            key_c = f"input{shutter.input_close}"
            val_o = payload.get(key_o, {}).get("value", False)
            val_c = payload.get(key_c, {}).get("value", False)

            # tylko gdy nie w trakcie ruchu
            if val_o and shutter.current_state != 'inprogress':
                control_shutter(shutter, 'open', self)
                self.pending.append({'id': shutter.id, 'action': 'inprogress', 'duration': shutter.open_duration})
            elif val_c and shutter.current_state != 'inprogress':
                control_shutter(shutter, 'close', self)
                self.pending.append({'id': shutter.id, 'action': 'inprogress', 'duration': shutter.close_duration})

    def publish(self, output_name, value):
        if not self.config:
            return
        pkt = {output_name: {"value": value}}
        self.client.publish(self.config.set_topic, json.dumps(pkt))

    def consume_pending_updates(self):
        buf = self.pending[:]
        self.pending.clear()
        return buf

mqtt_service = MQTTService()
