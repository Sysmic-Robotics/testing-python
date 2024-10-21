import serial
import time

from inputs import get_gamepad
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
    # Limitar el rango del número a 10 bits (incluyendo el bit de signo) (para V_x y V_y)
    return max(-512, min(511, numero))

def limitar_a_12_bits(numero):
    # Limitar el rango del número a 12 bits (incluyendo el bit de signo) (para V_th)
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
    return signo + (binario).zfill(longitud-1)

# Función para formar un trozo de 5 bytes con la estructura especificada
def formar_trozo(id_,dribb,kick, velocidad_x, velocidad_y, velocidad_th):
    #Se saturan los numeros a 10 bits (+511 -512) y 12 bits (+2047 -2048) respectivamente
    velocidad_x = limitar_a_10_bits(velocidad_x)
    velocidad_y = limitar_a_10_bits(velocidad_y)
    velocidad_th = limitar_a_12_bits(velocidad_th)

    a =  entero_a_binario(velocidad_x,10) 
    b = entero_a_binario(velocidad_y,10)
    c = entero_a_binario(velocidad_th,12)
    
    #print(a)
    #print(b)
    #print(c)   
    # Formar el trozo de 5 bytes
    trozo = bytearray([
        (((id_<<4)+dribb)<<1)+kick,  # Primer byte: id | dribb | kick
        int(a[0] + (a[3:]),2),  # segundo byte: signo | LSB Vx
        int(b[0] + (b[3:]),2),  # Tercer byte: signo | LSB Vy
        int(c[0] + (c[5:]),2),  # Cuarto byte: signo | LSB Vth
        int((a[1:3]) + (b[1:3]) + (c[1:5]),2)  # Quinto byte: MSB Vx | MSB Vy |MSB Vth  int(velocidad_x >> 6) | ((velocidad_y >> 6) << 2) | ((velocidad_th >> 4) << 4)
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


    def read(self): # return the buttons/triggers that you care about in this methode
        xL = self.LeftJoystickX
        xR = self.RightJoystickX
        yR = self.RightJoystickY
        return [xL, xR, yR]


    def _monitor_controller(self):
        while True:
            events = get_gamepad()
            for event in events:
                if event.code == 'ABS_Y':
                    self.LeftJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_X':
                    self.LeftJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_RY':
                    self.RightJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_RX':
                    self.RightJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_Z':
                    self.LeftTrigger = event.state / XboxController.MAX_TRIG_VAL # normalize between 0 and 1
                elif event.code == 'ABS_RZ':
                    self.RightTrigger = event.state / XboxController.MAX_TRIG_VAL # normalize between 0 and 1
                elif event.code == 'BTN_TL':
                    self.LeftBumper = event.state
                elif event.code == 'BTN_TR':
                    self.RightBumper = event.state
                elif event.code == 'BTN_SOUTH':
                    self.A = event.state
                elif event.code == 'BTN_NORTH':
                    self.Y = event.state #previously switched with X
                elif event.code == 'BTN_WEST':
                    self.X = event.state #previously switched with Y
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




#############################################################################################################################################################################################################
#############################################################################################################################################################################################################
#############################################################################################################################################################################################################




# Crear el buffer de 30 bytes
buffer = bytearray(30)

trozos = [
    formar_trozo(0b001,0,0,0,0,0),  # Trozo 1
    formar_trozo(0b010,0,0,0,0,0),   # Trozo 2
    formar_trozo(0b011,0,0,0,0,0),   # Trozo 3
    formar_trozo(0b100,0,0,0,0,0),  # Trozo 4
    formar_trozo(0b101,0,0,0,0,0),  # Trozo 5
    formar_trozo(0b110,0,0,0,0,0)   # Trozo 6
]
# Insertar los trozos en el buffer

for i in range(5):
    buffer[i*5:i*5+5] = trozos[i]






# Configurar el puerto serial
puerto_serial = serial.Serial('COM5', 115200, bytesize=8, parity='N', stopbits=1, timeout=1)

Vmax= 30

try:
    #rID = int(input("Ingrese ID de robto a controlar: "))
    print("ID del robot a controlar: 0")
    Vmax= int(input("Ingrese velocidad maxima del robot de 0 a 512 (max 150): "))
    if Vmax > 150:
        Vmax = 150
    elif Vmax < 0:
        Vmax = 0

    joy = XboxController()

    zona_muerta = 5

    while True:
        # Obtener las coordenadas del punto final y el tiempo de llegada deseado
        vels = joy.read()

        vX_A = vels[2]
        vY_A = vels[1]
        vTH_A = vels[0]

        vX = round(vX_A*Vmax)
        vY = round(vY_A*Vmax)
        vTH = round(vTH_A*Vmax)

        # aplicar zona muerta
        vX = aplicar_zona_muerta(vX, zona_muerta)
        vY = aplicar_zona_muerta(vY, zona_muerta)
        vTH = aplicar_zona_muerta(vTH, zona_muerta)

        # Limitar la velocidad a Vmax
        vX, vY = limitar_velocidad(vX, vY, Vmax)
        

         # Formar los trozos con las velocidades calculadas
        trozos = [
        formar_trozo(0b001,0,0,vX,vY,vTH),  # Trozo 1
        formar_trozo(0b010,0,0,0,0,0),   # Trozo 2
        formar_trozo(0b011,0,0,0,0,0),   # Trozo 3
        formar_trozo(0b100,0,0,0,0,0),  # Trozo 4
        formar_trozo(0b101,0,0,0,0,0),  # Trozo 5
        formar_trozo(0b110,0,0,0,0,0)   # Trozo 6
        ]       

        # Insertar los trozos en el buffer
        for i in range(6):
            buffer[i*5:i*5+5] = trozos[i]
        
        print(vX)
        puerto_serial.write(buffer)
        print("Paquete de datos enviado correctamente.")
        time.sleep(0.5)
        
        

except KeyboardInterrupt:
    print("\nPrograma terminado por el usuario.")
except serial.SerialException as e:
    print("Error al enviar el paquete de datos:", e)
finally:
    # Cerrar el puerto serial
    puerto_serial.close()

