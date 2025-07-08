
import serial
import struct
import time
import threading
import json


class SerialRx:
    def __init__(self, port='COM6', baudrate=460800):
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(port, baudrate, timeout=0.016)
        self.robots = {}

    def listen_once(self):
        packet_size = 32  # 1 byte header + 4 wheels * 4 bytes each
        if self.ser.in_waiting >= packet_size:
            data = self.ser.read(packet_size)
            self._parse_packet(data)

    def close(self):
        self.ser.close()

    def _parse_packet(self, data):
        if len(data) != 32:
            return
        header = data[0]
        robot_id = (header & 0b11100000) >> 5
        ball = bool(header & 0b00000001)
        wheels = []
        for i in range(4):
            start = 1 + i*4
            wheel_bytes = data[start:start+4]
            # Ahora asume float32 big endian (formato C float STM32)
            wheel_val = struct.unpack('<f', wheel_bytes)[0]
            wheels.append(wheel_val)
        timestamp = time.time()
        self.robots[robot_id] = {
            "ball_detected": ball,
            "wheels_meas": wheels,
            "timestamp": timestamp
        }

    def get_meas(self):
        return json.dumps(self.robots, indent=2)

if __name__ == "__main__":
    reader = SerialRx(port='COM6', baudrate=460800)
    try:
        last_print = time.time()
        while True:
            reader.listen_once()
            now = time.time()
            if now - last_print >= 0.5:
                print(reader.get_meas())
                last_print = now
    except KeyboardInterrupt:
        reader.close()
