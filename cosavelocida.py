import math

def calcular_velocidades(punto_final, tiempo, velocidad_maxima):
    # Punto inicial (suponiendo que el robot está en el origen)
    punto_inicial = (0, 0)

    # Calcula la distancia y el ángulo al punto final
    delta_x = punto_final[0] - punto_inicial[0]
    delta_y = punto_final[1] - punto_inicial[1]
    distancia = math.sqrt(delta_x**2 + delta_y**2)
    angulo = math.atan2(delta_y, delta_x)

    # Calcula las velocidades lineales (vx, vy) y la velocidad angular (v_theta)
    vx = delta_x / tiempo
    vy = delta_y / tiempo
    v_theta = angulo / tiempo

    # Verifica si la velocidad calculada excede la velocidad máxima
    velocidad_actual = math.sqrt(vx**2 + vy**2)
    if velocidad_actual > velocidad_maxima:
        escala = velocidad_maxima / velocidad_actual
        vx *= escala
        vy *= escala

    return vx, vy, v_theta

# Ejemplo de uso
punto_final = (5, 5)  # Coordenadas del punto final
tiempo = 2  # Tiempo en el que deseas que el robot llegue al punto final (segundos)
velocidad_maxima = 1  # Velocidad máxima del robot
vx, vy, v_theta = calcular_velocidades(punto_final, tiempo, velocidad_maxima)
print("Velocidad en x:", vx)
print("Velocidad en y:", vy)
print("Velocidad angular:", v_theta)

data = bytearray(buffer)

             # Convertir cada byte a binario y llenar con ceros a la izquierda para asegurar 8 bits
             binary_representation = [bin(byte)[2:].zfill(8) for byte in data]

              # Imprimir la representación binaria de cada byte
             for i, byte in enumerate(binary_representation):
                print(f'Byte {i}: {byte}')