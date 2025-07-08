#ifndef SERIALRX_HPP
#define SERIALRX_HPP

#include <QObject>
#include <QSerialPort>
#include <QVector>
#include <QMap>

struct RobotMeas {
    bool ball_detected;
    QVector<float> wheels_meas;
    double timestamp;
};

class SerialRx : public QObject {
    Q_OBJECT
public:
    explicit SerialRx(const QString& port = "COM6", int baudrate = 460800, QObject* parent = nullptr);
    ~SerialRx();
    void listenOnce();
    void close();
    // Acceso eficiente a los datos
    const QMap<int, RobotMeas>& getMeasures() const;

private:
    void parsePacket(const QByteArray& data);
    QSerialPort serial;
    QMap<int, RobotMeas> robots;
};

#endif // SERIALRX_HPP
