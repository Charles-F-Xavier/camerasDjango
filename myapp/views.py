import json
import os
import requests
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.core import serializers
from django.db import connection, OperationalError
from django.shortcuts import render
from django.http import HttpResponse
import math
from .models import Count
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

# Ruta al archivo de logs
LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'websocket.log')

def index(request):
    return render(request, 'myapp/index.html')


def login(request):
    return render(request, 'myapp/login.html')


# Función para conectarse al API y obtener los datos
def obtener_datos_vehiculos():
    # URL del endpoint de login
    login_url = "http://200.63.96.130:8088/StandardApiAction_login.action"
    login_params = {
        "account": "Administrador",
        "password": "7c6b75d80d0dc139126fbecdb67e0d91"
    }

    # Realizar la llamada al endpoint de login
    login_response = requests.get(login_url, params=login_params)

    # Verificar si la solicitud fue exitosa
    if login_response.status_code != 200:
        print("Error al realizar el login:", login_response.text)
        return None

    # Obtener la cookie JSESSIONID
    response_data=json.loads(login_response.text)
    jsession =response_data.get("JSESSIONID")

    if not jsession:
        print("No se pudo obtener el JSESSIONID.")
        return None

    # Usar JSESSIONID para realizar la solicitud de vehículos
    vehicle_url = "http://200.63.96.130:8088/StandardApiAction_queryUserVehicle.action"
    vehicle_params = {
        "jsession": jsession,
        "language": "en"
    }

    vehicle_response = requests.get(vehicle_url, params=vehicle_params)

    # Verificar si la solicitud fue exitosa
    if vehicle_response.status_code != 200:
        print("Error al obtener los datos de vehículos:", vehicle_response.text)
        return None

    # Retornar los datos en formato JSON
    return vehicle_response.json()


# Función para organizar el JSON en un árbol jerárquico
def organizar_json(data):
    # Crear la estructura raíz
    tree = {"Vtraxx": []}

    # Crear un diccionario de empresas basado en el ID
    empresas = {company["id"]: {"name": company["nm"], "vehicles": []} for company in data["companys"]}

    # Iterar sobre los vehículos para asociarlos a las empresas
    for vehicle in data["vehicles"]:
        empresa_id = vehicle["pid"]  # ID de la empresa a la que pertenece el vehículo
        if empresa_id in empresas:
            # Extraer los datos del vehículo
            vehicle_data = {
                "name": vehicle["nm"],
                "channels": []
            }

            # Separar los canales si están en una lista como "CH1, CH2, CH3, ..."
            if isinstance(vehicle["dl"], str):
                canales = vehicle["dl"].split(",")  # Separar por coma
                for canal in canales:
                    vehicle_data["channels"].append({"channel_id": canal.strip(), "channel_name": canal.strip()})
            else:
                for channel in vehicle["dl"]:
                    vehicle_data["channels"].append({
                        "channel_id": channel["id"],
                        "channel_name": channel["cn"].split(",")
                    })

            # Agregar el vehículo a la empresa correspondiente
            empresas[empresa_id]["vehicles"].append(vehicle_data)
<<<<<<< HEAD
=======

>>>>>>> parent of e62d9de (fix jsession)
    # Agregar las empresas al árbol
    tree["Vtraxx"] = list(empresas.values())

    return tree


def transformar_para_jstree(data):
    tree = []

    # Nodo raíz
    root_node = {"id": "vtraxx", "parent": "#", "text": "Vtraxx"}
    tree.append(root_node)

    for empresa in data["Vtraxx"]:
        # Crear el nodo para la empresa
        empresa_node = {"id": f"{empresa['name']}", "parent": "vtraxx", "text": empresa["name"]}
        tree.append(empresa_node)

        for vehiculo in empresa["vehicles"]:
            # Crear el nodo para el vehículo
            vehiculo_node = {"id": f"{vehiculo['name']}", "parent": f"{empresa['name']}",
                             "text": vehiculo["name"]}
            tree.append(vehiculo_node)

            for canal in vehiculo["channels"]:
<<<<<<< HEAD
                # Crear el nodo para el canal, asegurando un id único con el nombre del vehículo y el canal
                canal_node = {
                    "id": f"{canal['channel_id']}_{canal['channel_name']}",
                    # Combinando el id del canal y el nombre del vehículo
                    "parent": f"{vehiculo['name']}",
                    "text": canal["channel_name"]
                }
                tree.append(canal_node)
=======
                for ch_name in canal["channel_name"]:
                    # Crear el nodo para el canal
                    canal_node = {
                        "id": f"{canal['channel_id']}",
                        "parent": f"{vehiculo['name']}",
                        "text": ch_name
                    }
                    tree.append(canal_node)

>>>>>>> parent of e62d9de (fix jsession)
    return json.dumps(tree, indent=4)


# Función para generar el HTML a partir del JSON organizado
def generar_html(data):
    html_content = "<ul> id='tree-js'"  # Lista principal

    for empresa in data["Vtraxx"]:
        html_content += f"<li>Empresa: {empresa['name']}<ul>"  # Lista de vehículos

        for vehiculo in empresa["vehicles"]:
            html_content += f"<li>Vehículo: {vehiculo['name']}<ul>"  # Lista de canales

            for canal in vehiculo["channels"]:
                html_content += f"<li>Canal ID: {canal['channel_id']} - Canal: {canal['channel_name']}</li>"

            html_content += "</ul></li>"  # Cierre de la lista de canales

        html_content += "</ul></li>"  # Cierre de la lista de vehículos

    html_content += "</ul>"  # Cierre de la lista principal

    return html_content


# Vista para la página de inicio
def home(request):
    # captura de los dispotivos en la base de datos
    devices = Count.objects.values('device_id').distinct()

    # configuracion default de las camaras
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

    # n de camaras desde el request, si no 9
    camera_count = int(request.GET.get('camera_count', 9))
    camera_configs = camera_configs[:camera_count]
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
        'devices': devices,
        'tree': transformar_para_jstree(organizar_json(obtener_datos_vehiculos()))
    })


def dashboard(request):
    camera_data = Count.objects.all().order_by('date')

    data_serialized = serializers.serialize('json', camera_data)

    grouped_data=(
        Count.objects.annotate(date_only=TruncDate('date'))
        .values('date_only')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('date_only')
    )

    #crear datos para el pie chart
    pie_chart_data = [
        {"name":str(entry['date_only']),"value":entry['total_quantity']}
        for entry in grouped_data
    ]

    context = {
        'camera_data': camera_data,
        'data_seria': data_serialized,
        'chart_data': pie_chart_data,
    }
    # Pasar los datos al template
    return render(request, 'myapp/dashboard.html', context)


def monitoreo(request):
    # URL del endpoint de login
    login_url = "http://200.63.96.130:8088/StandardApiAction_login.action"
    login_params = {
        "account": "Administrador",
        "password": "7c6b75d80d0dc139126fbecdb67e0d91"
    }

    # Realizar la llamada al endpoint de login
    login_response = requests.get(login_url, params=login_params)

    # Verificar si la solicitud fue exitosa
    if login_response.status_code != 200:
        print("Error al realizar el login:", login_response.text)
        return None

    # Obtener la cookie JSESSIONID
    response_data = json.loads(login_response.text)
    jsession = response_data.get("JSESSIONID")

    if not jsession:
        print("No se pudo obtener el JSESSIONID.")
        return None


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
    camera_configs = camera_configs[:camera_count]
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


    return render(request, 'myapp/monitoreo.html', {
        'camera_count_range': camera_count_range,
        'cols': cols,
        'rows': rows,
        'camera_configs': camera_configs,
        'devices': devices,
        'jsession': jsession,
    })


@csrf_exempt
def log_error(request):
    if request.method == 'POST':
        try:
            # Parsear el cuerpo de la solicitud
            data = json.loads(request.body)
            error_message = data.get('error', 'No error message provided')
            camera_port = data.get('cameraPort', 'Unknown port')
            timestamp = data.get('timestamp', datetime.utcnow().isoformat())

            # Formatear el mensaje de log
            log_message = f"[{timestamp}] [Camera Port: {camera_port}] {error_message}\n"

            # Escribir en el archivo de logs
            with open(LOG_FILE_PATH, 'a') as log_file:
                log_file.write(log_message)

            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
<<<<<<< HEAD
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


def logout(request):
    return render(request, 'myapp/logout.html')
=======
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
>>>>>>> parent of e62d9de (fix jsession)
