import threading
import time
from ..models import Shutter


def _run_and_finalize(mqtt_service, relay_on, relay_off, duration, shutter_id):
    mqtt_service.publish(relay_on, True)
    time.sleep(duration)
    mqtt_service.publish(relay_on, False)
    mqtt_service.publish(relay_off, False)

    shutter = Shutter.objects.get(pk=shutter_id)
    # Determine final state based on which relay was on
    if relay_on.endswith(str(shutter.relay_open)):
        shutter.current_state = 'open'
    else:
        shutter.current_state = 'closed'
    shutter.save()


def _activate_cycle(mqtt_service, shutter_id, relay_on, relay_off, duration):
    # Ensure the opposite relay is off, then pulse the desired relay
    mqtt_service.publish(relay_off, False)
    mqtt_service.publish(relay_on, True)
    time.sleep(duration)
    mqtt_service.publish(relay_on, False)

    # Update the final state in the database
    shutter = Shutter.objects.get(pk=shutter_id)
    final_state = 'open' if relay_on == f"output{shutter.relay_open}" else 'closed'
    shutter.current_state = final_state
    shutter.save()

    # Notify frontend of completion
    mqtt_service.pending_updates.append({
        'id': shutter_id,
        'action': final_state,
        'duration': 0
    })


def control_shutter(shutter, action, mqtt_service):
    """
    Start an open or close cycle. Sets an intermediate state ('opening'/'closing'), saves it,
    then triggers the relay cycle in a background thread and updates the final state.
    """
    if action == 'open':
        relay_on = f"output{shutter.relay_open}"
        relay_off = f"output{shutter.relay_close}"
        duration = shutter.open_duration
        intermediate_state = 'opening'
    elif action == 'close':
        relay_on = f"output{shutter.relay_close}"
        relay_off = f"output{shutter.relay_open}"
        duration = shutter.close_duration
        intermediate_state = 'closing'
    else:
        raise ValueError("Nieznana akcja")

    # Set intermediate state and save
    shutter.current_state = intermediate_state
    shutter.save()

    # Notify frontend of the start
    mqtt_service.pending_updates.append({
        'id': shutter.id,
        'action': intermediate_state,
        'duration': duration
    })

    # Run the physical relay cycle in background
    thread = threading.Thread(
        target=_activate_cycle,
        args=(mqtt_service, shutter.id, relay_on, relay_off, duration),
        daemon=True
    )
    thread.start()
