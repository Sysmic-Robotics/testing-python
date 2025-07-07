import asyncio
import websockets
import json

async def test_websocket_client():
    """Cliente de prueba para WebSocket que muestra los datos de robots"""
    uri = "ws://localhost:8765"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Conectado al servidor WebSocket")
            print("📡 Escuchando datos de robots...")
            print("=" * 60)
            
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    
                    print(f"🕒 Timestamp: {data['timestamp']}")
                    
                    # Mostrar datos de cada robot
                    active_robots = 0
                    for robot_id, robot_data in data['robots'].items():
                        if robot_data['last_update']:
                            active_robots += 1
                            print(f"🤖 {robot_id}: vel1={robot_data['ang_vel_1']:6.2f}, "
                                  f"vel2={robot_data['ang_vel_2']:6.2f}, "
                                  f"vel3={robot_data['ang_vel_3']:6.2f}, "
                                  f"vel4={robot_data['ang_vel_4']:6.2f}")
                    
                    if active_robots == 0:
                        print("⚠️  No hay robots activos")
                    else:
                        print(f"📊 Robots activos: {active_robots}/6")
                    
                    print("-" * 60)
                    
                except websockets.exceptions.ConnectionClosed:
                    print("❌ Conexión WebSocket cerrada")
                    break
                except json.JSONDecodeError as e:
                    print(f"❌ Error al decodificar JSON: {e}")
                    
    except ConnectionRefusedError:
        print("❌ No se pudo conectar al servidor WebSocket")
        print("💡 Asegúrate de que receptorRX.py esté ejecutándose")
    except Exception as e:
        print(f"❌ Error en cliente WebSocket: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando cliente de prueba WebSocket...")
    asyncio.run(test_websocket_client())
