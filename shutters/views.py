from django.shortcuts import render, get_object_or_404, redirect
from .models import Shutter, MQTTConfig
from .forms import MQTTConfigForm
from django.http import JsonResponse
from .actions.shutter_actions import control_shutter
from .mqtt_client import mqtt_service

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json


def index(request):
    shutters = Shutter.objects.all()
    return render(request, 'shutters/index.html', {'shutters': shutters})


def control_shutter_view(request, shutter_id, action):
    shutter = get_object_or_404(Shutter, pk=shutter_id)
    control_shutter(shutter, action, mqtt_service)
    return JsonResponse({'status': f'{action} command sent to {shutter.name}'})


def mqtt_settings(request):
    config = MQTTConfig.objects.first() or MQTTConfig()
    if request.method == 'POST':
        form = MQTTConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = MQTTConfigForm(instance=config)

    return render(request, 'shutters/mqtt_settings.html', {'form': form})


@require_POST
@csrf_exempt
def update_times(request, shutter_id):
    shutter = get_object_or_404(Shutter, pk=shutter_id)
    data = json.loads(request.body)
    shutter.open_duration = data.get('open_duration', shutter.open_duration)
    shutter.close_duration = data.get('close_duration', shutter.close_duration)
    shutter.save()
    return JsonResponse({'status': 'updated'})


def get_shutter_updates(request):
    """
    Zwraca listę pending updates z MQTTService.consume_pending_updates(),
    np. [{ 'id': 1, 'action': 'inprogress', 'duration': 5 }, …]
    """
    updates = mqtt_service.consume_pending_updates()
    return JsonResponse(updates, safe=False)
