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
            console.error(`Video element with id ${videoElementId} not found`);
            return;
        }

        this.connectionState = {
            isConnecting: false,
            shouldReconnect: true
        };

        if (this.cameraPort) {
            this.connect();
        } else {
            console.error('Puerto inválido:', cameraPort);
        }
    }

    // Método para extraer el número del puerto
    extractPort(portText) {
        // Buscar un número de 4 dígitos que comience con 8
        const portMatch = portText.match(/\b8\d{3}\b/);
        if (portMatch) {
            return portMatch[0];
        }
        console.error('No se pudo extraer el puerto del texto:', portText);
        return null;
    }

    async connect() {
        if (this.connectionState.isConnecting || this.isConnected) {
            return;
        }

        this.connectionState.isConnecting = true;

        try {
            console.log(`Intentando conectar a ${this.connectionUrl}`);
            
            if (this.ws) {
                this.ws.close();
                this.ws = null;
            }

            this.ws = new WebSocket(this.connectionUrl);
            this.setupWebSocketHandlers();
            
            await new Promise((resolve, reject) => {
                const timeout = setTimeout(() => {
                    reject(new Error('Timeout connecting to WebSocket'));
                }, 5000);

                this.ws.onopen = () => {
                    clearTimeout(timeout);
                    resolve();
                };

                this.ws.onerror = (error) => {
                    clearTimeout(timeout);
                    reject(error);
                };
            });

        } catch (error) {
            console.error(`Error connecting to WebSocket: ${error.message}`);
            this.handleReconnection();
        } finally {
            this.connectionState.isConnecting = false;
        }
    }

    setupWebSocketHandlers() {
        this.ws.onopen = () => {
            console.log(`Connected to camera feed on port ${this.cameraPort}`);
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.videoElement.classList.add('connected');
            
            // Enviar mensaje inicial
            this.sendMessage({ type: 'init' });
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.frame) {
                    this.videoElement.src = `data:image/jpeg;base64,${data.frame}`;
                    
                    const counterElement = document.getElementById(`people-count-${this.cameraPort}`);
                    if (counterElement && data.count !== undefined) {
                        counterElement.textContent = `${data.count}`;
                    }
                }
            } catch (error) {
                console.error('Error processing message:', error);
            }
        };

        this.ws.onclose = (event) => {
            console.log(`WebSocket closed. Code: ${event.code}, Reason: ${event.reason}`);
            this.isConnected = false;
            this.videoElement.classList.remove('connected');
            
            if (this.connectionState.shouldReconnect) {
                this.handleReconnection();
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            if (this.ws.readyState === WebSocket.OPEN) {
                this.ws.close();
            }
        };
    }

    handleReconnection() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('Max reconnection attempts reached');
            this.connectionState.shouldReconnect = false;
            return;
        }

        this.reconnectAttempts++;
        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
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


function initializeVideoFeeds() {
    console.log('Initializing video feeds...');
    const cameras = document.querySelectorAll('.camera');
    
    cameras.forEach(camera => {
        // Buscar el puerto en el texto del overlay
        const portElement = camera.querySelector('.card-img-overlay');
        const videoElement = camera.querySelector('.camera-image');
        
        if (portElement && videoElement) {
            const portText = portElement.textContent.trim();
            console.log(`Initializing camera with port text: "${portText}" and video element ID ${videoElement.id}`);
            new WebSocketVideoHandler(portText, videoElement.id);
        } else {
            console.error('Missing required elements for camera:', camera);
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing video feeds...');
    initializeVideoFeeds();
});