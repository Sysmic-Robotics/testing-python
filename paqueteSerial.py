import serial
import time

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


try:
    while True:
          # Obtener las coordenadas del punto final y el tiempo de llegada deseado
        vx = int(input("Ingrese velocidad en x: "))
        vy = int(input("Ingrese velocidad en y: "))
        vth = int(input("Ingrese velocidad en theta: "))
        tiempo_funcionamiento = int(input("Ingrese el tiempo de funcionamiento en segundos: "))
       
        max_acc_vx = 10
        max_acc_vy = 5
        max_acc_vth = 5
        time_vx,num_step_vx = calcularTiempo(vx,max_acc_vx)
        time_vy,num_step_vy = calcularTiempo(vy,max_acc_vy)
        time_vth,num_step_vth = calcularTiempo(vth,max_acc_vth)

        vx_steps =cacularVelocidades_step(vx,max_acc_vx,num_step_vx)
        vy_steps =cacularVelocidades_step(vy,max_acc_vy,num_step_vy)
        vth_steps =cacularVelocidades_step(vth,max_acc_vth,num_step_vth)
        for step in range(max(num_step_vx,num_step_vy,num_step_vth)+1 ):
            if step < len(vx_steps):
                vX = int(round(vx_steps[step]))
            else:
                vX = vx
            if step <len(vy_steps):
                vY = int(round(vy_steps[step]))
            else:
                vY = vy
            if step <len(vth_steps):
                vTH = int(round(vth_steps[step]))
            else:
                vTH = vth 

                

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
            print(buffer)
            time.sleep(0.1)
        for step in range(max(num_step_vx,num_step_vy,num_step_vth)+1 ):
            if step < len(vx_steps):
                vX = int(round(vx_steps[num_step_vx - step]))
            else:
                vX = vx
            if step <len(vy_steps):
                vY = int(round(vy_steps[num_step_vy - step]))
            else:
                vY = vy
            if step <len(vth_steps):
                vTH = int(round(vth_steps[num_step_vth - step]))
            else:
                vTH = vth 

                

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
            print(buffer)
            time.sleep(0.1)


        a=[]
        

        print("Paquete de datos STOP enviado correctamente.")
        time.sleep(tiempo_funcionamiento)  # Esperar un tiempo antes de apagarse
        

except KeyboardInterrupt:
    print("\nPrograma terminado por el usuario.")
except serial.SerialException as e:
    print("Error al enviar el paquete de datos:", e)
finally:
    # Cerrar el puerto serial
    puerto_serial.close()

