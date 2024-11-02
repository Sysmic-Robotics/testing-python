import serial
import struct

# Configuración del puerto serial
port = 'COM8'
baud_rate = 115200  # Cambia si es necesario
ser = serial.Serial(port, baud_rate, timeout=1)

while True:
    if ser.in_waiting >= 32:  # Espera hasta recibir 32 bytes
        # Lee los 32 bytes del paquete
        data = ser.read(32)
        #print("Datos crudos recibidos:", data)  # Verifica que tienes 32 bytes

        # Extrae cada float individualmente
        try:
            ang_vel_1 = struct.unpack('<f', data[0:4])[0]
            ang_vel_2 = struct.unpack('<f', data[4:8])[0]
            ang_vel_3 = struct.unpack('<f', data[8:12])[0]
            ang_vel_4 = struct.unpack('<f', data[12:16])[0]

            # Imprime cada valor de velocidad angular para confirmar
            print("Velocidades angulares:")
            print("Rueda 1:", ang_vel_1)
            print("Rueda 2:", ang_vel_2)
            print("Rueda 3:", ang_vel_3)
            print("Rueda 4:", ang_vel_4)

        except struct.error as e:
            print("Error al desempaquetar:", e)

ser.close()
