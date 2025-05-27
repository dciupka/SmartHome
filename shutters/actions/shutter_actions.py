import threading
import time
from ..models import Shutter

def _run_and_finalize(mqtt_service, relay_on, relay_off, duration, shutter_id):
    mqtt_service.publish(relay_on, True)
    time.sleep(duration)
    mqtt_service.publish(relay_on, False)
    mqtt_service.publish(relay_off, False)

    shutter = Shutter.objects.get(pk=shutter_id)
    shutter.current_state = 'open' if relay_on.endswith(str(shutter.relay_open)) else 'closed'
    shutter.save()

def control_shutter(shutter: Shutter, action: str, mqtt_service):
    if action == 'open':
        relay_on  = f"output{shutter.relay_open}"
        relay_off = f"output{shutter.relay_close}"
        duration  = shutter.open_duration
    elif action == 'close':
        relay_on  = f"output{shutter.relay_close}"
        relay_off = f"output{shutter.relay_open}"
        duration  = shutter.close_duration
    else:
        raise ValueError("Nieznana akcja")

    # stan pośredni
    shutter.current_state = 'inprogress'
    shutter.save()

    # wykonanie ruchu w tle
    threading.Thread(
        target=_run_and_finalize,
        args=(mqtt_service, relay_on, relay_off, duration, shutter.id),
        daemon=True
    ).start()
