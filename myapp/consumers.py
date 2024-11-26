# consumers.py
import asyncio
import json
import base64
import cv2
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer


class CameraFeedConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.camera = None
        self.send_task = None
        self.is_streaming = False

    async def connect(self):
        logging.info("Nueva conexión WebSocket entrante")
        await self.accept()
        self.is_streaming = True
        # Iniciar la tarea de streaming
        self.send_task = asyncio.create_task(self.stream_camera())
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "Conexión WebSocket establecida"
        }))

    async def disconnect(self, close_code):
        logging.info(f"WebSocket desconectado con código: {close_code}")
        self.is_streaming = False
        if self.send_task:
            self.send_task.cancel()
        if self.camera and self.camera.is_open():
            self.camera.release()
        raise StopConsumer()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            logging.info(f"Mensaje recibido: {data}")

            if data.get('type') == 'start_stream':
                channel = data.get('channel', 0)
                await self.start_camera_stream(channel)
            elif data.get('type') == 'stop_stream':
                await self.stop_camera_stream()

        except Exception as e:
            logging.error(f"Error en receive: {str(e)}")
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": str(e)
            }))

    async def start_camera_stream(self, channel):
        try:
            if self.camera is None or not self.camera.is_open():
                self.camera = cv2.VideoCapture(channel)
                if not self.camera.is_open():
                    raise Exception("No se pudo abrir la cámara")

            await self.send(text_data=json.dumps({
                "type": "stream_started",
                "message": "Transmisión iniciada"
            }))

        except Exception as e:
            logging.error(f"Error iniciando stream: {str(e)}")
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": f"Error iniciando stream: {str(e)}"
            }))

    async def stop_camera_stream(self):
        try:
            if self.camera and self.camera.is_open():
                self.camera.release()
                self.camera = None
            await self.send(text_data=json.dumps({
                "type": "stream_stopped",
                "message": "Transmisión detenida"
            }))
        except Exception as e:
            logging.error(f"Error deteniendo stream: {str(e)}")

    async def stream_camera(self):
        try:
            while self.is_streaming:
                if self.camera and self.camera.is_open():
                    ret, frame = self.camera.read()
                    if ret:
                        # Redimensionar el frame si es necesario
                        frame = cv2.resize(frame, (640, 480))

                        # Convertir a JPEG
                        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])

                        # Convertir a base64
                        base64_frame = base64.b64encode(buffer).decode('utf-8')

                        # Enviar frame
                        await self.send(text_data=json.dumps({
                            "type": "frame",
                            "frame": base64_frame
                        }))

                        # Pequeña pausa para controlar la tasa de frames
                        await asyncio.sleep(0.033)  # Aproximadamente 30 FPS
                    else:
                        logging.warning("No se pudo leer el frame")
                        await asyncio.sleep(1)
                else:
                    await asyncio.sleep(1)

        except Exception as e:
            logging.error(f"Error en stream_camera: {str(e)}")