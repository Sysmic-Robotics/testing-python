import serial
import serial.tools.list_ports
import time

from inputs import get_gamepad, devices
import math
import threading
import numpy as np

def calcularTiempo(Vtarget,max_acc):
    tiempo_necesitado = abs(Vtarget/max_acc)
    num_steps = int(tiempo_necesitado*1)
    return tiempo_necesitado, num_steps

def cacularVelocidades_step(Vtarget,max_acc,num_steps):
    velocities =[]
    step_acc = max_acc
    
    for step in range(num_steps+1):
            v_current = step*step_acc
            if v_current > abs(Vtarget):
                v_current = Vtarget
            if Vtarget < 0:
                v_current=-int(round(v_current))
            v_current=int(round(v_current))
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
    binario = bin(n)[2:]  # Convertir a binario y eliminar el prefijo '0b'
    return signo + binario.zfill(longitud - 1)

def formar_trozo(id_,dribb,kick, velocidad_x, velocidad_y, velocidad_th):
    velocidad_x = limitar_a_10_bits(velocidad_x)
    velocidad_y = limitar_a_10_bits(velocidad_y)
    velocidad_th = limitar_a_12_bits(velocidad_th)

    a =  entero_a_binario(velocidad_x,10) 
    b = entero_a_binario(velocidad_y,10)
    c = entero_a_binario(velocidad_th,12)
    
    trozo = bytearray([
        (((id_ << 4) + dribb) << 1) + kick,
        int(a[0] + a[3:], 2),
        int(b[0] + b[3:], 2),
        int(c[0] + c[5:], 2),
        int(a[1:3] + b[1:3] + c[1:5], 2)
    ])
    return trozo

class XboxController(threading.Thread):
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    def __init__(self, index):
        threading.Thread.__init__(self)
        self.index = index
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

    def readInputs(self):
        return [self.LeftJoystickX, self.RightJoystickX, self.RightJoystickY,self.RightTrigger]

    def _monitor_controller(self):
        while True:
            if self.index < len(devices.gamepads):
                events = devices.gamepads[self.index].read()
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
            else:
                print(f"Gamepad index {self.index} is out of range. Available gamepads: {len(devices.gamepads)}")
                time.sleep(1)

def aplicar_zona_muerta(valor, zona_muerta):
    if abs(valor) < zona_muerta:
        return 0
    return valor

def limitar_velocidad(vX, vY, Vmax):
    magnitud = math.sqrt(vX**2 + vY**2)
    if magnitud > Vmax:
        factor = Vmax / magnitud
        vX *= factor
        vY *= factor
    return int(vX), int(vY)

def detectar_puerto_serial():
    puertos = list(serial.tools.list_ports.comports())
    for puerto in puertos:
        if "FTDI" in puerto.manufacturer:
            return puerto.device
    raise Exception("No se encontró un puerto serial adecuado.")

buffer = bytearray(30)

trozos = [
    formar_trozo(0b001,0,0,0,0,0),
    formar_trozo(0b010,0,0,0,0,0),
    formar_trozo(0b011,0,0,0,0,0),
    formar_trozo(0b100,0,0,0,0,0),
    formar_trozo(0b101,0,0,0,0,0),
    formar_trozo(0b110,0,0,0,0,0)
]

for i in range(5):
    buffer[i*5:i*5+5] = trozos[i]

# Configurar el puerto serial
#puerto_serial = serial.Serial('COM9', 115200, bytesize=8, parity='N', stopbits=1, timeout=1)
try:
    puerto_dispositivo = detectar_puerto_serial()
    puerto_serial = serial.Serial(puerto_dispositivo, 115200, bytesize=8, parity='N', stopbits=1, timeout=1)
    print(f"Puerto serial {puerto_dispositivo} abierto correctamente.")
except serial.SerialException as e:
    print(f"Error al abrir el puerto serial: {e}")
except Exception as e:
    print(f"Error: {e}")

Vmax= 30
zona_muerta = 10

try:
    while True:
        try:
            rID1 = int(input("Ingrese el primer ID de robot a controlar (0-5): "))
            rID2 = int(input("Ingrese el segundo ID de robot a controlar (0-5): "))
            if rID1 == rID2:
                raise ValueError("Los IDs de los robots no pueden ser iguales.")
            if not (0 <= rID1 <= 5) or not (0 <= rID2 <= 5):
                raise ValueError("Los IDs deben estar entre 0 y 5.")
            break
        except ValueError as e:
            print(f"Error: {e}. Por favor, intente de nuevo.")

    while True:
        try:
            Vmax = int(input("Ingrese velocidad maxima del robot de 0 a 512 (capado a 150): "))
            if Vmax > 150:
                Vmax = 150
            elif Vmax < 0:
                Vmax = 0
            break
        except ValueError:
            print("Error: La velocidad máxima debe ser un número entero. Por favor, intente de nuevo.")

    joy1 = XboxController(0)
    joy2 = XboxController(1)
    
    while True:
        vels1 = joy1.readInputs()
        vels2 = joy2.readInputs()

        vX_A1 = vels1[2]
        vY_A1 = vels1[1]
        vTH_A1 = vels1[0]
        drib1 = vels1[3]

        vX_A2 = vels2[2]
        vY_A2 = vels2[1]
        vTH_A2 = vels2[0]
        drib2 = vels2[3]

        vX1 = round(vX_A1*Vmax)
        vY1 = round(vY_A1*Vmax)
        vTH1 = round(vTH_A1*Vmax)
        drib1 = round(drib1)

        vX2 = round(vX_A2*Vmax)
        vY2 = round(vY_A2*Vmax)
        vTH2 = round(vTH_A2*Vmax)
        drib2 = round(drib2)

        vX1 = aplicar_zona_muerta(vX1, zona_muerta)
        vY1 = aplicar_zona_muerta(vY1, zona_muerta)
        vTH1 = aplicar_zona_muerta(vTH1, zona_muerta)

        vX2 = aplicar_zona_muerta(vX2, zona_muerta)
        vY2 = aplicar_zona_muerta(vY2, zona_muerta)
        vTH2 = aplicar_zona_muerta(vTH2, zona_muerta)


        
        vX1, vY1 = limitar_velocidad(vX1, vY1, Vmax)
        vX2, vY2 = limitar_velocidad(vX2, vY2, Vmax)


        #mapear driblers entre 0 a 7 y redondear
        drib1 = round(drib1*7)
        drib2 = round(drib2*7)


        trozos = []

        for i in range(6):
            if i == rID1:
                trozos.append(formar_trozo(i+1,drib1,0,vX1,vY1,vTH1))
            elif i == rID2:
                trozos.append(formar_trozo(i+1,drib2,0,vX2,vY2,vTH2))
            else:
                trozos.append(formar_trozo(0b001,0,0,0,0,0))

        print(f"trozos: {trozos}")  # Debugging line

        for i in range(6):
            buffer[i*5:i*5+5] = trozos[i]
        
        print(f"vX1: {vX1}, vY1: {vY1}, vTH1: {vTH1}")  # Debugging line
        print(f"vX2: {vX2}, vY2: {vY2}, vTH2: {vTH2}")


        puerto_serial.write(buffer)
        print("Paquete de datos enviado correctamente.\n")
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nPrograma terminado por el usuario.")
except serial.SerialException as e:
    print("Error al enviar el paquete de datos:", e)
finally:
    # Cerrar el puerto serial
    puerto_serial.close()



    print("Puerto serial cerrado correctamente.")