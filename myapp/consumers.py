# consumers.py
import asyncio
import json
import base64
import cv2
import frame
import websockets
from channels.generic.websocket import AsyncWebsocketConsumer


class CameraFeedConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Aceptar la conexión WebSocket
        await self.accept()
        await self.send(text_data=json.dumps({
            "message": "Conexión WebSocket establecida"
        }))

    async def disconnect(self, close_code):
        # Lógica para manejar desconexión
        print(f"WebSocket desconectado con código: {close_code}")

    async def receive(self, text_data):
        # Manejar los mensajes enviados desde el cliente
        data = json.loads(text_data)
        print(f"Mensaje recibido: {data}")

        # Responder al cliente
        await self.send(text_data=json.dumps({
            "message": "Mensaje recibido",
            "data": data
        }))

    async def test_websocket(self):
        uri = "ws://127.0.0.1:8002/ws"
        try:
            async with websockets.connect(uri) as websocket:
                print("Conexión establecida")
                await websocket.send("hello")
                response = await websocket.recv()
                print(f"Respuesta del servidor: {response}")
        except Exception as e:
            print(f"Error conectando al WebSocket: {e}")
