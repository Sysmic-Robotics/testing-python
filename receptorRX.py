import serial
import struct
import asyncio
import websockets
import json
import threading
import time
from datetime import datetime
from typing import Dict, List, Any

class RobotDataReader:
    def __init__(self, port='COM10', baud_rate=115200, websocket_port=8765):
        self.port = port
        self.baud_rate = baud_rate
        self.websocket_port = websocket_port
        
        # Datos de los 6 robots
        self.robots_data = {
            f'robot_{i}': {
                'id': i,
                'timestamp': None,
                'ang_vel_1': 0.0,
                'ang_vel_2': 0.0,
                'ang_vel_3': 0.0,
                'ang_vel_4': 0.0,
                'last_update': None
            } for i in range(6)
        }
        
        # Control de hilos
        self.running = True
        self.ser = None
        self.connected_clients = set()
        
    def init_serial(self):
        """Inicializar conexión serial"""
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            print(f"Puerto serial {self.port} abierto correctamente")
            return True
        except serial.SerialException as e:
            print(f"Error al abrir puerto serial: {e}")
            return False
    
    def parse_robot_data(self, data: bytes, robot_id: int):
        """Parsear datos de 32 bytes para un robot específico"""
        try:
            # Extraer 4 floats de 32 bytes
            ang_vel_1 = struct.unpack('<f', data[0:4])[0]
            ang_vel_2 = struct.unpack('<f', data[4:8])[0] 
            ang_vel_3 = struct.unpack('<f', data[8:12])[0]
            ang_vel_4 = struct.unpack('<f', data[12:16])[0]
            
            # Actualizar datos del robot
            robot_key = f'robot_{robot_id}'
            current_time = datetime.now()
            
            self.robots_data[robot_key].update({
                'timestamp': current_time.isoformat(),
                'ang_vel_1': ang_vel_1,
                'ang_vel_2': ang_vel_2,
                'ang_vel_3': ang_vel_3,
                'ang_vel_4': ang_vel_4,
                'last_update': current_time
            })
            
            print(f"Robot {robot_id}: {ang_vel_1:.2f}, {ang_vel_2:.2f}, {ang_vel_3:.2f}, {ang_vel_4:.2f}")
            
        except struct.error as e:
            print(f"Error al parsear datos del robot {robot_id}: {e}")
    
    def serial_reader_thread(self):
        """Hilo para leer datos del puerto serial"""
        robot_counter = 0
        
        while self.running:
            try:
                if self.ser and self.ser.in_waiting >= 32:
                    # Lee 32 bytes del paquete
                    data = self.ser.read(32)
                    
                    if len(data) == 32:
                        # Rotar entre robots (0-5)
                        self.parse_robot_data(data, robot_counter % 6)
                        robot_counter += 1
                    
                time.sleep(0.001)  # Pequeña pausa para no saturar CPU
                
            except Exception as e:
                print(f"Error en lectura serial: {e}")
                time.sleep(1)
    
    def get_all_robots_data(self) -> Dict[str, Any]:
        """Obtener todos los datos de robots con timestamp global"""
        return {
            'timestamp': datetime.now().isoformat(),
            'robots': dict(self.robots_data)
        }
    
    async def websocket_handler(self, websocket, path):
        """Manejar conexiones WebSocket"""
        self.connected_clients.add(websocket)
        print(f"Cliente WebSocket conectado. Total: {len(self.connected_clients)}")
        
        try:
            await websocket.wait_closed()
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.connected_clients.discard(websocket)
            print(f"Cliente WebSocket desconectado. Total: {len(self.connected_clients)}")
    
    async def broadcast_data(self):
        """Enviar datos a todos los clientes conectados"""
        while self.running:
            if self.connected_clients:
                data_package = self.get_all_robots_data()
                message = json.dumps(data_package, indent=2)
                
                # Enviar a todos los clientes conectados
                disconnected = set()
                for client in self.connected_clients:
                    try:
                        await client.send(message)
                    except websockets.exceptions.ConnectionClosed:
                        disconnected.add(client)
                
                # Remover clientes desconectados
                self.connected_clients -= disconnected
            
            await asyncio.sleep(0.1)  # Enviar cada 100ms
    
    async def start_websocket_server(self):
        """Iniciar servidor WebSocket"""
        server = await websockets.serve(
            self.websocket_handler, 
            "localhost", 
            self.websocket_port
        )
        print(f"Servidor WebSocket iniciado en ws://localhost:{self.websocket_port}")
        
        # Iniciar broadcast de datos
        await asyncio.gather(
            server.wait_closed(),
            self.broadcast_data()
        )
    
    def start(self):
        """Iniciar el sistema completo"""
        # Inicializar puerto serial
        if not self.init_serial():
            return
        
        # Iniciar hilo de lectura serial
        serial_thread = threading.Thread(target=self.serial_reader_thread)
        serial_thread.daemon = True
        serial_thread.start()
        
        print("Sistema iniciado. Presiona Ctrl+C para detener.")
        print(f"WebSocket disponible en: ws://localhost:{self.websocket_port}")
        print("Datos disponibles en tiempo real vía WebSocket")
        
        try:
            # Iniciar servidor WebSocket
            asyncio.run(self.start_websocket_server())
        except KeyboardInterrupt:
            print("\nDeteniendo sistema...")
        finally:
            self.stop()
    
    def stop(self):
        """Detener el sistema"""
        self.running = False
        if self.ser:
            self.ser.close()
        print("Sistema detenido correctamente.")

# Función para crear cliente de prueba
async def test_websocket_client():
    """Cliente de prueba para WebSocket"""
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            print("Conectado al servidor WebSocket")
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                print(f"Datos recibidos: {data['timestamp']}")
                # Mostrar datos de cada robot
                for robot_id, robot_data in data['robots'].items():
                    if robot_data['last_update']:
                        print(f"  {robot_id}: velocidades {robot_data['ang_vel_1']:.2f}, {robot_data['ang_vel_2']:.2f}, {robot_data['ang_vel_3']:.2f}, {robot_data['ang_vel_4']:.2f}")
                print("-" * 50)
    except Exception as e:
        print(f"Error en cliente WebSocket: {e}")

if __name__ == "__main__":
    # Crear y iniciar el lector de datos
    reader = RobotDataReader(port='COM10', baud_rate=115200, websocket_port=8765)
    reader.start()