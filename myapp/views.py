from django.core import serializers
from django.db import connection, OperationalError
from django.shortcuts import render

from django.http import HttpResponse
import math

from .models import Count


# Create your views here.
# Vista para la página de inicio
def home(request):
    devices = Count.objects.values('device_id').distinct()
    camera_configs = [
        {'port': 8001, 'name': 'CH1'},
        {'port': 8002, 'name': 'CH2'},
        {'port': 8003, 'name': 'CH3'},
        {'port': 8004, 'name': 'CH4'},
        {'port': 8005, 'name': 'CH5'},
        {'port': 8006, 'name': 'CH6'},
        {'port': 8007, 'name': 'CH7'},
        {'port': 8008, 'name': 'CH8'},
        {'port': 8009, 'name': 'CH9'},
    ]

    camera_count = int(request.GET.get('camera_count', 9))
    camera_configs= camera_configs[:camera_count]
    if camera_count == 1:
        cols = 1
        rows = 1
    elif camera_count == 2:
        cols = 2
        rows = 1
    elif 3 <= camera_count <= 4:
        cols = 2
        rows = 2
    elif 5 <= camera_count <= 6:
        cols = 3
        rows = 2
    elif 7 <= camera_count <= 9:
        cols = 3
        rows = 3
    else:
        # Para más de 9 cámaras, se utiliza un cálculo general basado en la raíz cuadrada
        cols = math.ceil(math.sqrt(camera_count))
        rows = math.ceil(camera_count / cols)

    camera_count_range = range(1, camera_count + 1)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Si la solicitud es AJAX, devuelve solo el HTML para las cámaras
        return render(request, 'myapp/camera_display.html', {
            'camera_count_range': camera_count_range,
            'cols': cols,
            'rows': rows,
            'camera_configs': camera_configs,
            'devices': devices
        })

    # Si no es AJAX, devuelve la página completa
    return render(request, 'myapp/home.html', {
        'camera_count_range': camera_count_range,
        'cols': cols,
        'rows': rows,
        'camera_configs': camera_configs,
        'devices': devices
    })


def dashboard(request):
    camera_data = Count.objects.all().order_by('date')

    data_serialized = serializers.serialize('json', camera_data)

    context = {
        'camera_data': camera_data,
        'data_seria': data_serialized
    }
    # Pasar los datos al template
    return render(request, 'myapp/dashboard.html', context)
