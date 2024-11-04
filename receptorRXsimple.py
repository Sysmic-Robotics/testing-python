import serial
import struct
import matplotlib.pyplot as plt
import numpy as np

# Configuración del puerto serial
port = 'COM10'
baud_rate = 115200  # Cambia si es necesario
ser = serial.Serial(port, baud_rate, timeout=1)

# Inicializa las listas para almacenar los datos
ang_vel_1_list = []
ang_vel_2_list = []
ang_vel_3_list = []
ang_vel_4_list = []

# Configura el gráfico
plt.ion()
fig, ax = plt.subplots()
line1, = ax.plot([], [], label='ang_vel_1')
line2, = ax.plot([], [], label='ang_vel_2')
line3, = ax.plot([], [], label='ang_vel_3')
line4, = ax.plot([], [], label='ang_vel_4')
ax.legend()

# Define el rango esperado para los valores de velocidad angular
min_value = -1000.0
max_value = 1000.0

# Función para filtrar datos artefacto
def filtrar_artefactos(valor, min_val, max_val):
    if min_val <= valor <= max_val:
        return valor
    else:
        return valor

# Función para aplicar un filtro pasa bajos (media móvil)
def filtro_pasa_bajos(data_list, window_size=5):
    if len(data_list) < window_size:
        return data_list
    return np.convolve(data_list, np.ones(window_size)/window_size, mode='valid').tolist()

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

            # Filtrar datos artefacto
            ang_vel_1 = filtrar_artefactos(ang_vel_1, min_value, max_value)
            ang_vel_2 = filtrar_artefactos(ang_vel_2, min_value, max_value)
            ang_vel_3 = filtrar_artefactos(ang_vel_3, min_value, max_value)
            ang_vel_4 = filtrar_artefactos(ang_vel_4, min_value, max_value)

            # Añade los nuevos datos a las listas si no son artefactos
            if ang_vel_1 is not None:
                ang_vel_1_list.append(ang_vel_1)
            if ang_vel_2 is not None:
                ang_vel_2_list.append(ang_vel_2)
            if ang_vel_3 is not None:
                ang_vel_3_list.append(ang_vel_3)
            if ang_vel_4 is not None:
                ang_vel_4_list.append(ang_vel_4)

            # Aplica el filtro pasa bajos
            ang_vel_1_list_filtrada = filtro_pasa_bajos(ang_vel_1_list)
            ang_vel_2_list_filtrada = filtro_pasa_bajos(ang_vel_2_list)
            ang_vel_3_list_filtrada = filtro_pasa_bajos(ang_vel_3_list)
            ang_vel_4_list_filtrada = filtro_pasa_bajos(ang_vel_4_list)

            # Actualiza los datos del gráfico
            line1.set_data(range(len(ang_vel_1_list_filtrada)), ang_vel_1_list_filtrada)
            line2.set_data(range(len(ang_vel_2_list_filtrada)), ang_vel_2_list_filtrada)
            line3.set_data(range(len(ang_vel_3_list_filtrada)), ang_vel_3_list_filtrada)
            line4.set_data(range(len(ang_vel_4_list_filtrada)), ang_vel_4_list_filtrada)
            ax.relim()
            ax.autoscale_view()

            # Redibuja el gráfico
            fig.canvas.draw()
            fig.canvas.flush_events()

            # Imprime cada valor de velocidad angular para confirmar
            print("Velocidades angulares:")
            print("Rueda 1:", ang_vel_1)
            print("Rueda 2:", ang_vel_2)
            print("Rueda 3:", ang_vel_3)
            print("Rueda 4:", ang_vel_4)

            # Simula un retardo
            plt.pause(0.005)

        except struct.error as e:
            print("Error al desempaquetar:", e)

ser.close()