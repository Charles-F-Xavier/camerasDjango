class WebSocketVideoHandler {
    constructor(cameraPort, videoElementId) {
        this.ws = null;
        this.cameraPort = this.extractPort(cameraPort);
        this.videoElement = document.getElementById(videoElementId);
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;
        this.connectionUrl = `ws://127.0.0.1:${this.cameraPort}/ws`;

        if (!this.videoElement) {
            this.logError(`Video element with id ${videoElementId} not found`);
            return;
        }

        this.connectionState = {
            isConnecting: false,
            shouldReconnect: true
        };

        if (this.cameraPort) {
            this.connect();
        } else {
            this.logError('Puerto inválido:', cameraPort);
        }
    }

    // Método para extraer el número del puerto
    extractPort(portText) {
        const portMatch = portText.match(/\b8\d{3}\b/);
        if (portMatch) {
            return portMatch[0];
        }
        this.logError('No se pudo extraer el puerto del texto:', portText);
        return null;
    }

    logError(...args) {
        const message = args.join(' ');
        //console.error(message); // Opcional: Puedes comentar esta línea si no quieres mostrar los errores en la consola.

        // Enviar el error al backend
        fetch('/log-error/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                error: message,
                cameraPort: this.cameraPort,
                timestamp: new Date().toISOString()
            })
        }).catch((err) => {
            //console.error('Error al enviar el log al servidor:', err);
        });
    }

    async connect() {
        if (this.connectionState.isConnecting || this.isConnected) {
            return;
        }

        this.connectionState.isConnecting = true;

        try {
            //console.log(`Intentando conectar a ${this.connectionUrl}`);

            // Cerrar la conexión anterior si existe
            if (this.ws) {
                this.ws.close();
                this.ws = null;
            }

            // Intentar crear el WebSocket
            this.ws = new WebSocket(this.connectionUrl);

            // Configurar los handlers del WebSocket
            this.setupWebSocketHandlers();

            // Espera para la conexión con un timeout
            await new Promise((resolve, reject) => {
                const timeout = setTimeout(() => {
                    reject(new Error('Timeout connecting to WebSocket'));
                }, 5000); // Timeout de 5 segundos para la conexión

                this.ws.onopen = () => {
                    clearTimeout(timeout);
                    resolve();
                };

                this.ws.onerror = (error) => {
                    clearTimeout(timeout);
                    reject(error);  // Rechazar la promesa en caso de error
                    this.logError('Error connecting to WebSocket:', error);
                };
            });
        } catch (error) {
            // Capturar el error y evitar que se imprima en consola
            this.logError(`Error connecting to WebSocket: ${error.message}`);
            // Manejo de reconexión si es necesario
            this.handleReconnection();
        } finally {
            // Finalizar el estado de conexión
            this.connectionState.isConnecting = false;
        }
    }


    setupWebSocketHandlers() {
        this.ws.onopen = () => {
            //console.log(`Connected to camera feed on port ${this.cameraPort}`);
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.videoElement.classList.add('connected');

            // Actualiza el estado de la cámara a "Online"
            const statusDotElement = document.getElementById(`status-dot-${this.cameraPort}`);
            const statusElement = document.getElementById(`status-text-${this.cameraPort}`);

            if (statusDotElement && statusElement) {
                statusDotElement.style.backgroundColor = 'green'; // Punto verde cuando está online
                statusElement.textContent = 'Conectado';  // Texto de estado
            }

            // Enviar mensaje inicial
            this.sendMessage({type: 'init'});
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.frame) {
                    this.videoElement.src = `data:image/jpeg;base64,${data.frame}`;

                    const counterElement = document.getElementById(`people-count-${this.cameraPort}`);
                    const statusDotElement = document.getElementById(`status-dot-${this.cameraPort}`);
                    const statusElement = document.getElementById(`status-text-${this.cameraPort}`);

                    if (statusDotElement && statusElement) {
                        statusDotElement.style.backgroundColor = 'green'; // Punto verde cuando está online
                        statusElement.textContent = 'Conectado';  // Texto de estado
                    }

                    if (counterElement && data.count !== undefined) {
                        counterElement.textContent = `${data.count}`;
                    }
                }
            } catch (error) {
                this.logError('Error processing message:', error);
            }
        };

        this.ws.onclose = (event) => {
            this.logError(`WebSocket closed. Code: ${event.code}, Reason: ${event.reason}`);
            this.isConnected = false;
            this.videoElement.classList.remove('connected');

            // Actualiza el estado de la cámara a "Offline"
            const statusDotElement = document.getElementById(`status-dot-${this.cameraPort}`);
            const statusElement = document.getElementById(`status-text-${this.cameraPort}`);

            if (statusDotElement && statusElement) {
                statusDotElement.style.backgroundColor = 'red'; // Punto rojo cuando está offline
                statusElement.textContent = 'Desconectado';  // Texto de estado
            }

            if (this.connectionState.shouldReconnect) {
                this.handleReconnection();
            }
        };

        this.ws.onerror = (error) => {
            this.logError('WebSocket error:', error);
            if (this.ws.readyState === WebSocket.OPEN) {
                this.ws.close();
            }
        };
    }

    handleReconnection() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            this.logError('Max reconnection attempts reached');
            this.connectionState.shouldReconnect = false;
            return;
        }

        this.reconnectAttempts++;
        //console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

        const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1);
        setTimeout(() => this.connect(), delay);
    }

    sendMessage(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }

    disconnect() {
        this.connectionState.shouldReconnect = false;
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Objeto global para almacenar las conexiones WebSocket por puerto
const videoHandlers = {};

function initializeVideoFeeds() {
    //console.log('Initializing video feeds...');
    const cameras = document.querySelectorAll('.camera');

    cameras.forEach(camera => {
        const portElement = camera.querySelector('.card-img-overlay');
        const videoElement = camera.querySelector('.camera-image');

        if (portElement && videoElement) {
            const portText = portElement.textContent.trim();
            //console.log(`Initializing camera with port text: "${portText}" and video element ID ${videoElement.id}`);

            // Crear una instancia del manejador de video y almacenarla
            const handler = new WebSocketVideoHandler(portText, videoElement.id);
            videoHandlers[portText] = handler; // Guardar por puerto
        } else {
            this.logError('Missing required elements for camera:', camera);
            //console.error('Missing required elements for camera:', camera);
        }
    });
}

function sendDevidnoToServer(devidno) {
    // Encuentra cualquier WebSocket activo en el objeto videoHandlers
    const handlerKeys = Object.keys(videoHandlers);
    if (handlerKeys.length > 0) {
        const handler = videoHandlers[handlerKeys[0]]; // Usar la primera conexión activa
        if (handler.ws && handler.ws.readyState === WebSocket.OPEN) {
            const message = JSON.stringify({type: 'select_devino', devidno: devidno});
            handler.ws.send(message);
            //console.log(`Enviado al servidor: ${message}`);
        } else {
            //console.error('No se pudo enviar el devidno. WebSocket no está conectado.');
        }
    } else {
        //console.error('No hay instancias de WebSocket disponibles.');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    //console.log('DOM loaded, initializing video feeds...');
    initializeVideoFeeds();
});
