import json
import paho.mqtt.client as mqtt
from .models import MQTTConfig, Shutter
from .actions.shutter_actions import control_shutter


class MQTTService:
    def __init__(self):
        self.client = mqtt.Client()
        self.config = MQTTConfig.objects.first()

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
                shutter.refresh_from_db()  # aktualny stan rolety

                input_open_key = f"input{shutter.input_open}"
                input_close_key = f"input{shutter.input_close}"

                input_open_triggered = state_data.get(input_open_key, {}).get("value", False)
                input_close_triggered = state_data.get(input_close_key, {}).get("value", False)

                # **Blokada fizycznych wejść, gdy roleta w ruchu**
                if shutter.current_state in ['opening', 'closing']:
                    continue

                if input_open_triggered and shutter.current_state not in ['open', 'opening']:
                    print(f"Input open triggered for {shutter.name}")
                    control_shutter(shutter, 'open', self)
                    self.pending_updates.append({'id': shutter.id, 'action': 'open', 'duration': shutter.open_duration})

                elif input_close_triggered and shutter.current_state not in ['closed', 'closing']:
                    print(f"Input close triggered for {shutter.name}")
                    control_shutter(shutter, 'close', self)
                    self.pending_updates.append(
                        {'id': shutter.id, 'action': 'close', 'duration': shutter.close_duration})

        except Exception as e:
            print("State parse error:", e)

    def publish(self, output_name, value):
        if self.config:
            payload = json.dumps({output_name: {"value": value}})
            self.client.publish(self.config.set_topic, payload)
            print(f"MQTT publish → {self.config.set_topic}: {payload}")


mqtt_service = MQTTService()
