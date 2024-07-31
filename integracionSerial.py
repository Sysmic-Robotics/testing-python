import serial
import time
import threading
from inputs import get_gamepad
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from threading import Thread

def calcularTiempo(Vtarget, max_acc):
    tiempo_necesitado = abs(Vtarget / max_acc)
    num_steps = int(tiempo_necesitado * 1)
    return tiempo_necesitado, num_steps

def cacularVelocidades_step(Vtarget, max_acc, num_steps):
    velocities = []
    step_acc = max_acc

    for step in range(num_steps + 1):
        v_current = step * step_acc
        if v_current > abs(Vtarget):
            v_current = Vtarget
        if Vtarget < 0:
            v_current = -int(round(v_current))
        v_current = int(round(v_current))
        velocities.append(v_current)
    return velocities

def limitar_a_10_bits(numero):
    return max(-512, min(511, numero))

def limitar_a_12_bits(numero):
    return max(-2048, min(2047, numero))

def entero_a_binario(n, longitud):
    if n == 0:
        return '0' * longitud
    signo = '0' if n >= 0 else '1'
    n = abs(n)
    binario = ''
    while n > 0:
        binario = str(n % 2) + binario
        n //= 2
    return signo + (binario).zfill(longitud - 1)

def formar_trozo(id_, dribb, kick, velocidad_x, velocidad_y, velocidad_th):
    velocidad_x = limitar_a_10_bits(velocidad_x)
    velocidad_y = limitar_a_10_bits(velocidad_y)
    velocidad_th = limitar_a_12_bits(velocidad_th)

    a = entero_a_binario(velocidad_x, 10)
    b = entero_a_binario(velocidad_y, 10)
    c = entero_a_binario(velocidad_th, 12)

    trozo = bytearray([
        (((id_ << 4) + dribb) << 1) + kick,
        int(a[0] + (a[3:]), 2),
        int(b[0] + (b[3:]), 2),
        int(c[0] + (c[5:]), 2),
        int((a[1:3]) + (b[1:3]) + (c[1:5]), 2)
    ])
    return trozo

class XboxController(object):
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    def __init__(self):
        self.LeftJoystickY = 0
        self.LeftJoystickX = 0
        self.RightJoystickY = 0
        self.RightJoystickX = 0
        self.LeftTrigger = 0
        self.RightTrigger = 0
        self.LeftBumper = 0
        self.RightBumper = 0
        self.A = 0
        self.X = 0
        self.Y = 0
        self.B = 0
        self.LeftThumb = 0
        self.RightThumb = 0
        self.Back = 0
        self.Start = 0
        self.LeftDPad = 0
        self.RightDPad = 0
        self.UpDPad = 0
        self.DownDPad = 0

        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def read(self):
        xL = self.LeftJoystickX
        xR = self.RightJoystickX
        yR = self.RightJoystickY
        return [xL, xR, yR]

    def _monitor_controller(self):
        while True:
            events = get_gamepad()
            for event in events:
                if event.code == 'ABS_Y':
                    self.LeftJoystickY = event.state / XboxController.MAX_JOY_VAL
                elif event.code == 'ABS_X':
                    self.LeftJoystickX = event.state / XboxController.MAX_JOY_VAL
                elif event.code == 'ABS_RY':
                    self.RightJoystickY = event.state / XboxController.MAX_JOY_VAL
                elif event.code == 'ABS_RX':
                    self.RightJoystickX = event.state / XboxController.MAX_JOY_VAL
                elif event.code == 'ABS_Z':
                    self.LeftTrigger = event.state / XboxController.MAX_TRIG_VAL
                elif event.code == 'ABS_RZ':
                    self.RightTrigger = event.state / XboxController.MAX_TRIG_VAL
                elif event.code == 'BTN_TL':
                    self.LeftBumper = event.state
                elif event.code == 'BTN_TR':
                    self.RightBumper = event.state
                elif event.code == 'BTN_SOUTH':
                    self.A = event.state
                elif event.code == 'BTN_NORTH':
                    self.Y = event.state
                elif event.code == 'BTN_WEST':
                    self.X = event.state
                elif event.code == 'BTN_EAST':
                    self.B = event.state
                elif event.code == 'BTN_THUMBL':
                    self.LeftThumb = event.state
                elif event.code == 'BTN_THUMBR':
                    self.RightThumb = event.state
                elif event.code == 'BTN_SELECT':
                    self.Back = event.state
                elif event.code == 'BTN_START':
                    self.Start = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY1':
                    self.LeftDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY2':
                    self.RightDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY3':
                    self.UpDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY4':
                    self.DownDPad = event.state

# Configuración del puerto serial
puerto_serial_tx = serial.Serial('COM5', 115200, bytesize=8, parity='N', stopbits=1, timeout=1)
serial_port_rx = 'COM12'
baud_rate = 115200
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

def init():
    for line in lines.values():
        line.set_data([], [])
    return lines.values()

def update(frame):
    global time_data, velocities

    for wheel, line in lines.items():
        line.set_data(time_data, velocities[wheel])
    ax.relim()
    ax.autoscale_view()
    return lines.values()

def read_serial():
    global time_data, velocities

    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            wheel_1, wheel_2, wheel_3, wheel_4 = map(float, data.split(','))

            time_data.append(time.time())
            velocities['wheel_1'].append(wheel_1)
            velocities['wheel_2'].append(wheel_2)
            velocities['wheel_3'].append(wheel_3)
            velocities['wheel_4'].append(wheel_4)

            if len(time_data) > 100:
                time_data = time_data[-100:]
                for key in velocities.keys():
                    velocities[key] = velocities[key][-100:]

def tx_controller():
    buffer = bytearray(30)
    trozos = [formar_trozo(0b001, 0, 0, 0, 0, 0), formar_trozo(0b010, 0, 0, 0, 0, 0), formar_trozo(0b011, 0, 0, 0, 0, 0),
              formar_trozo(0b100, 0, 0, 0, 0, 0), formar_trozo(0b101, 0, 0, 0, 0, 0), formar_trozo(0b110, 0, 0, 0, 0, 0)]
    for i in range(5):
        buffer[i * 5:i * 5 + 5] = trozos[i]

    Vmax = 30

    try:
        rID = int(input("Ingrese ID de robot a controlar: "))
        Vmax = int(input("Ingrese velocidad máxima del robot de 0 a 512: "))
        joy = XboxController()
        while True:
            vels = joy.read()

            vX_A = vels[2]
            vY_A = vels[1]
            vTH_A = vels[0]

            vX = round(vX_A * Vmax)
            vY = round(vY_A * Vmax)
            vTH = round(vTH_A * Vmax)

            trozos = [formar_trozo(0b001, 0, 0, vX, vY, vTH), formar_trozo(0b010, 0, 0, 0, 0, 0),
                      formar_trozo(0b011, 0, 0, 0, 0, 0), formar_trozo(0b100, 0, 0, 0, 0, 0),
                      formar_trozo(0b101, 0, 0, 0, 0, 0), formar_trozo(0b110, 0, 0, 0, 0, 0)]

            for i in range(6):
                buffer[i * 5:i * 5 + 5] = trozos[i]

            print(vX)
            puerto_serial_tx.write(buffer)
            print("Paquete de datos enviado correctamente.")
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nPrograma terminado por el usuario.")
    except serial.SerialException as e:
        print("Error al enviar el paquete de datos:", e)
    finally:
        puerto_serial_tx.close()

# Iniciar el hilo para la recepción de datos seriales
serial_thread = Thread(target=read_serial)
serial_thread.daemon = True
serial_thread.start()

# Iniciar el hilo para el controlador del TX
tx_thread = Thread(target=tx_controller)
tx_thread.daemon = True
tx_thread.start()

# Animación del gráfico
ani = animation.FuncAnimation(fig, update, init_func=init, blit=True)
plt.show()
