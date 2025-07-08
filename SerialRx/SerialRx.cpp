#include "SerialRx.hpp"
#include <QDateTime>
#include <QDataStream>
#include <cstring>

SerialRx::SerialRx(const QString& port, int baudrate, QObject* parent)
    : QObject(parent) {
    serial.setPortName(port);
    serial.setBaudRate(baudrate);
    serial.setDataBits(QSerialPort::Data8);
    serial.setParity(QSerialPort::NoParity);
    serial.setStopBits(QSerialPort::OneStop);
    serial.setFlowControl(QSerialPort::NoFlowControl);
    serial.open(QIODevice::ReadOnly);
}

SerialRx::~SerialRx() {
    close();
}

void SerialRx::listenOnce() {
    const int packet_size = 32;
    if (serial.bytesAvailable() >= packet_size) {
        QByteArray data = serial.read(packet_size);
        parsePacket(data);
    }
}

void SerialRx::close() {
    if (serial.isOpen()) {
        serial.close();
    }
}

void SerialRx::parsePacket(const QByteArray& data) {
    if (data.size() != 32) return;
    quint8 header = static_cast<quint8>(data[0]);
    int robot_id = (header & 0b11100000) >> 5;
    bool ball = (header & 0b00000001) != 0;
    QVector<float> wheels;
    for (int i = 0; i < 4; ++i) {
        float wheel_val;
        std::memcpy(&wheel_val, data.constData() + 1 + i * 4, 4);
        wheels.append(wheel_val);
    }
    double timestamp = QDateTime::currentDateTimeUtc().toMSecsSinceEpoch() / 1000.0;
    robots[robot_id] = RobotMeas{ball, wheels, timestamp};
}

const QMap<int, RobotMeas>& SerialRx::getMeasures() const {
    return robots;
}
