import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from threading import Thread
import time

# Configuración del puerto serial
serial_port_rx = 'COM12'  # Reemplaza 'COMX' con el puerto adecuado
baud_rate = 115200  # Ajusta el baud rate si es necesario
ser = serial.Serial(serial_port_rx, baud_rate)

# Variables para almacenar los datos de las velocidades
velocities = {'wheel_1': [], 'wheel_2': [], 'wheel_3': [], 'wheel_4': []}
time_data = []

# Inicialización del gráfico
fig, ax = plt.subplots()
lines = {
    'wheel_1': ax.plot([], [], label='Wheel 1')[0],
    'wheel_2': ax.plot([], [], label='Wheel 2')[0],
    'wheel_3': ax.plot([], [], label='Wheel 3')[0],
    'wheel_4': ax.plot([], [], label='Wheel 4')[0]
}
ax.set_xlim(0, 100)
ax.set_ylim(-100, 100)
ax.legend()
#papas fritas

def init():
    for line in lines.values():
        line.set_data([], [])
    return lines.values()

def update(frame):
    global time_data, velocities

    # Actualización de los datos del gráfico
    for wheel, line in lines.items():
        line.set_data(time_data, velocities[wheel])
    ax.relim()
    ax.autoscale_view()
    return lines.values()

def read_serial():
    global time_data, velocities
    while True:
        if ser.in_waiting > 0:
            data = ser.readline()
            print(data)
            wheel_1, wheel_2, wheel_3, wheel_4 = map(float, data.split(','))

            # Actualizar datos
            time_data.append(time.time())
            velocities['wheel_1'].append(wheel_1)
            velocities['wheel_2'].append(wheel_2)
            velocities['wheel_3'].append(wheel_3)
            velocities['wheel_4'].append(wheel_4)

            # Limitar el tamaño de los datos almacenados
            if len(time_data) > 100:
                time_data = time_data[-100:]
                for key in velocities.keys():
                    velocities[key] = velocities[key][-100:]

# Hilo para leer los datos del puerto serial
serial_thread = Thread(target=read_serial)
serial_thread.daemon = True
serial_thread.start()

# Animación del gráfico
ani = animation.FuncAnimation(fig, update, init_func=init, blit=True)
plt.show()
