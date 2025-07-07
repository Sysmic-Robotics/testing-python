# 🤖 Sistema de Lectura de Datos de Robots via Serial y WebSocket

Este sistema lee datos de 6 robots desde un puerto serial USB (COM10) y los expone en tiempo real a través de WebSocket para que otros procesos puedan consumirlos.

## 📋 Características

- ✅ Lectura continua de datos seriales de 6 robots
- ✅ Parsing de paquetes de 32 bytes con 4 velocidades angulares por robot
- ✅ Timestamps automáticos para cada actualización
- ✅ Servidor WebSocket para distribución de datos en tiempo real
- ✅ Manejo de múltiples clientes WebSocket simultáneos
- ✅ Gestión robusta de errores y reconexiones

## 🚀 Archivos Principales

### `receptorRX.py`
Sistema principal que:
- Lee datos del puerto serial COM10 a 115200 baud
- Mantiene datos actualizados de 6 robots con timestamps
- Expone datos vía WebSocket en puerto 8765
- Maneja rotación automática entre robots

### `test_websocket_client.py`
Cliente de prueba para verificar el funcionamiento del WebSocket

### `simulate_serial_data.py`
Simulador de datos seriales para pruebas sin hardware

## 📦 Estructura de Datos

### Entrada Serial (32 bytes por paquete)
Cada paquete contiene 4 valores float (4 bytes cada uno):
- `ang_vel_1`: Velocidad angular rueda 1
- `ang_vel_2`: Velocidad angular rueda 2  
- `ang_vel_3`: Velocidad angular rueda 3
- `ang_vel_4`: Velocidad angular rueda 4

### Salida WebSocket (JSON)
```json
{
  "timestamp": "2025-07-06T10:30:45.123456",
  "robots": {
    "robot_0": {
      "id": 0,
      "timestamp": "2025-07-06T10:30:45.123456",
      "ang_vel_1": 25.67,
      "ang_vel_2": -12.34,
      "ang_vel_3": 0.00,
      "ang_vel_4": 45.89,
      "last_update": "datetime_object"
    },
    "robot_1": { ... },
    ...
    "robot_5": { ... }
  }
}
```

## 🔧 Instalación

1. Instalar dependencias:
```bash
pip install pyserial websockets
```

2. Verificar puerto serial (cambiar en código si es necesario):
```python
port = 'COM10'  # Windows
# port = '/dev/ttyUSB0'  # Linux
# port = '/dev/tty.usbserial-xxx'  # macOS
```

## 🎯 Uso

### 1. Iniciar el sistema principal:
```bash
python receptorRX.py
```

Salida esperada:
```
Puerto serial COM10 abierto correctamente
Sistema iniciado. Presiona Ctrl+C para detener.
WebSocket disponible en: ws://localhost:8765
Datos disponibles en tiempo real vía WebSocket
Servidor WebSocket iniciado en ws://localhost:8765
Robot 0: 25.67, -12.34, 0.00, 45.89
Robot 1: 15.23, 8.91, -5.67, 12.45
...
```

### 2. Probar conexión WebSocket:
```bash
python test_websocket_client.py
```

### 3. (Opcional) Simular datos para pruebas:
```bash
python simulate_serial_data.py
```

## 🌐 Integración con Otros Procesos

### Cliente WebSocket básico:
```python
import asyncio
import websockets
import json

async def robot_data_consumer():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            # Procesar datos de robots
            for robot_id, robot_info in data['robots'].items():
                if robot_info['last_update']:
                    print(f"Robot {robot_info['id']}: velocidades disponibles")
                    # Tu lógica aquí...

asyncio.run(robot_data_consumer())
```

### Cliente HTTP/REST (alternativa):
Si prefieres HTTP sobre WebSocket, puedes modificar el sistema para exponer un endpoint REST.

## ⚙️ Configuración

### Parámetros del RobotDataReader:
```python
reader = RobotDataReader(
    port='COM10',           # Puerto serial
    baud_rate=115200,       # Velocidad de transmisión
    websocket_port=8765     # Puerto WebSocket
)
```

### Frecuencia de envío:
- Lectura serial: Continua (1ms de pausa)
- Broadcast WebSocket: 100ms (10 Hz)

## 🔍 Monitoreo y Debug

### Logs del sistema:
- Conexiones/desconexiones de clientes WebSocket
- Datos recibidos por robot con timestamps
- Errores de parsing o comunicación

### Métricas disponibles:
- Número de clientes WebSocket conectados
- Última actualización por robot
- Estado de conexión serial

## 🛠️ Solución de Problemas

### Puerto serial no disponible:
```
Error al abrir puerto serial: [Errno 2] No such file or directory: 'COM10'
```
- Verificar que el dispositivo esté conectado
- Comprobar el puerto correcto en el Administrador de dispositivos (Windows)
- Cambiar permisos del puerto (Linux/macOS)

### WebSocket no conecta:
- Verificar que el puerto 8765 esté libre
- Comprobar firewall local
- Usar `localhost` en lugar de IP externa

### Datos inconsistentes:
- Verificar formato de paquetes seriales (32 bytes)
- Comprobar endianness (`<f` = little-endian float)
- Validar que el baud rate coincida con el emisor

## 📈 Próximas Mejoras

- [ ] Logging a archivo con rotación
- [ ] Métricas de rendimiento (latencia, throughput)
- [ ] API REST complementaria
- [ ] Dashboard web en tiempo real
- [ ] Almacenamiento histórico en base de datos
- [ ] Compresión de datos para WebSocket
- [ ] Autenticación para clientes WebSocket

## 🤝 Integración con Sysmic Engine

Este sistema está diseñado para trabajar independientemente del sysmic-engine, permitiendo:
- Pruebas aisladas de comunicación
- Desarrollo paralelo de componentes
- Debugging específico de datos seriales
- Validación de protocolos de comunicación

---

**Desarrollado para el proyecto Sysmic** 🏆
