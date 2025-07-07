import struct
import random
import time
import serial

def simulate_robot_data():
    """Simula datos de un robot con 4 velocidades angulares"""
    # Generar velocidades aleatorias entre -100 y 100
    ang_vel_1 = random.uniform(-100.0, 100.0)
    ang_vel_2 = random.uniform(-100.0, 100.0)
    ang_vel_3 = random.uniform(-100.0, 100.0)
    ang_vel_4 = random.uniform(-100.0, 100.0)
    
    # Empaquetar como 4 floats en little-endian (32 bytes total)
    data = struct.pack('<ffff', ang_vel_1, ang_vel_2, ang_vel_3, ang_vel_4)
    
    # Rellenar hasta 32 bytes si es necesario
    data += b'\x00' * (32 - len(data))
    
    return data

def simulate_serial_data_sender(port='COM10', baud_rate=115200):
    """
    Simulador de datos seriales para pruebas
    NOTA: Esto requiere un puerto serial virtual o hardware real
    """
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"📡 Simulador iniciado en {port}")
        print("🤖 Enviando datos simulados de 6 robots...")
        
        robot_id = 0
        while True:
            # Simular datos para un robot
            data = simulate_robot_data()
            
            print(f"📤 Enviando datos del robot {robot_id}: {len(data)} bytes")
            ser.write(data)
            
            # Alternar entre robots 0-5
            robot_id = (robot_id + 1) % 6
            
            time.sleep(0.1)  # Enviar cada 100ms
            
    except serial.SerialException as e:
        print(f"❌ Error al abrir puerto serial {port}: {e}")
        print("💡 Para usar este simulador necesitas:")
        print("   1. Un puerto serial virtual (com0com, etc.)")
        print("   2. O hardware serial real conectado")
    except KeyboardInterrupt:
        print("\n🛑 Simulador detenido por el usuario")
        if 'ser' in locals():
            ser.close()

def test_data_parsing():
    """Prueba local del parsing de datos"""
    print("🧪 Probando parsing de datos simulados...")
    
    for robot_id in range(6):
        # Simular datos
        data = simulate_robot_data()
        
        # Parsear como lo hace receptorRX.py
        ang_vel_1 = struct.unpack('<f', data[0:4])[0]
        ang_vel_2 = struct.unpack('<f', data[4:8])[0]
        ang_vel_3 = struct.unpack('<f', data[8:12])[0]
        ang_vel_4 = struct.unpack('<f', data[12:16])[0]
        
        print(f"Robot {robot_id}: {ang_vel_1:.2f}, {ang_vel_2:.2f}, {ang_vel_3:.2f}, {ang_vel_4:.2f}")
        
    print("✅ Parsing completado correctamente")

if __name__ == "__main__":
    print("🔧 Simulador de datos seriales para robots")
    print("=" * 50)
    
    # Primero probar el parsing localmente
    test_data_parsing()
    print()
    
    # Luego intentar simular por puerto serial
    simulate_serial_data_sender()
