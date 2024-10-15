## Repositorio
Estos codigos tienen como finalidad testear de forma interna diferentes aspectos del envio y recepcion de datos a los robots, sin necesidad del uso del sysmic-engine.

## controllerSerial.py

Este archivo permite controlar un robot con ID del 0 al 5, a una velocidad maxima dada.

### requiere:
- control xbox usb
- Tx baste station

### Velocidades
Los paquetes permiten una velocidad máxima de 511 por eje (no se en que unidad se encuentra).  

Vel recomendada: 50
Vel rápida: 150 (genera daños en la estructura del robot)

### Base Station
Se debe conectar en el puerto USB correcto ya que la direccion de este se encuentra descrita en texto palno en el codigo (COM5)
