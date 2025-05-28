import json
import threading
import paho.mqtt.client as mqtt
from .models import MQTTConfig, Shutter
from .actions.shutter_actions import control_shutter

class MQTTService:
    def __init__(self):
        self.client = mqtt.Client()
        self.config = MQTTConfig.objects.first()
        self.pending_updates = []

        if self.config:
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.connect(self.config.broker_address, self.config.broker_port)
            self.client.subscribe(self.config.state_topic)
            self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("MQTT connected")

    def on_message(self, client, userdata, msg):
        print(f"MQTT Message received: {msg.topic} {msg.payload}")
        try:
            state_data = json.loads(msg.payload.decode())

            for shutter in Shutter.objects.all():
                shutter.refresh_from_db()

                open_key = f"input{shutter.input_open}" if shutter.input_open else None
                close_key = f"input{shutter.input_close}" if shutter.input_close else None

                open_trig = open_key and state_data.get(open_key, {}).get("value", False)
                close_trig = close_key and state_data.get(close_key, {}).get("value", False)

                # Blokujemy open jeśli otwarte lub otwierające się
                if open_trig:
                    if shutter.current_state not in ['open', 'opening']:
                        print(f"Input open triggered for {shutter.name}")
                        control_shutter(shutter, 'open', self)
                        self.pending_updates.append({'id': shutter.id, 'action': 'opening', 'duration': shutter.open_duration})
                    else:
                        print(f"Ignored open input for {shutter.name} (state={shutter.current_state})")

                # Blokujemy close jeśli zamknięte lub zamykające się
                if close_trig:
                    if shutter.current_state not in ['closed', 'closing']:
                        print(f"Input close triggered for {shutter.name}")
                        control_shutter(shutter, 'close', self)
                        self.pending_updates.append({'id': shutter.id, 'action': 'closing', 'duration': shutter.close_duration})
                    else:
                        print(f"Ignored close input for {shutter.name} (state={shutter.current_state})")

        except Exception as e:
            print("State parse error:", e)

    def publish(self, output_name, value):
        if self.config:
            payload = json.dumps({output_name: {"value": value}})
            self.client.publish(self.config.set_topic, payload)
            print(f"MQTT publish → {self.config.set_topic}: {payload}")

    def consume_pending_updates(self):
        updates = self.pending_updates[:]
        self.pending_updates.clear()
        return updates

mqtt_service = MQTTService()
