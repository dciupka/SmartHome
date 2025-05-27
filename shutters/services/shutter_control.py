from ..mqtt_client import mqtt_service
import threading
import time

def activate_output_temporarily(output, duration):
    mqtt_service.publish(output, True)
    time.sleep(duration)
    mqtt_service.publish(output, False)

def control_shutter(shutter, action):
    if action == 'open':
        relay_on = f"output{shutter.relay_open}"
        relay_off = f"output{shutter.relay_close}"
        duration = shutter.open_duration
    elif action == 'close':
        relay_on = f"output{shutter.relay_close}"
        relay_off = f"output{shutter.relay_open}"
        duration = shutter.close_duration
    else:
        raise ValueError("Nieznana akcja")

    mqtt_service.publish(relay_off, False)
    thread = threading.Thread(target=activate_output_temporarily, args=(relay_on, duration))
    thread.start()


def control_shutter(shutter, action):
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
    threading.Thread(target=activate_output_temporarily, args=(relay_on, duration)).start()


def control_shutter(shutter, action):
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
    threading.Thread(target=activate_output_temporarily, args=(relay_on, duration)).start()
