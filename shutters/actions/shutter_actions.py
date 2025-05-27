import threading
import time

def activate_output_temporarily(mqtt_service, output, duration):
    mqtt_service.publish(output, True)
    time.sleep(duration)
    mqtt_service.publish(output, False)

def control_shutter(shutter, action, mqtt_service):
    if action == 'open':
        relay_on = f"output{shutter.relay_open}"
        relay_off = f"output{shutter.relay_close}"
        duration = shutter.open_duration
        shutter.current_state = 'open'
    elif action == 'close':
        relay_on = f"output{shutter.relay_close}"
        relay_off = f"output{shutter.relay_open}"
        duration = shutter.close_duration
        shutter.current_state = 'closed'
    else:
        raise ValueError("Nieznana akcja")

    shutter.save()
    mqtt_service.publish(relay_off, False)
    threading.Thread(target=activate_output_temporarily, args=(mqtt_service, relay_on, duration)).start()
