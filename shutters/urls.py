from django.urls import path
from . import views

app_name = 'shutters'

urlpatterns = [
    path('', views.index, name='index'),
    path('mqtt/settings/', views.mqtt_settings, name='mqtt_settings'),
    path('shutter/status/', views.get_shutter_updates, name='get_shutter_updates'),
    # Ważne: najpierw specyficzne
    path('shutter/<int:shutter_id>/update_times/', views.update_times, name='update_times'),
    # Na końcu ogólne z <str:action>
    path('shutter/<int:shutter_id>/<str:action>/', views.control_shutter_view, name='control_shutter'),

]
