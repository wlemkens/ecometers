import datetime as dt
import serial
import threading
import time
import logging

class Datagram:
    SETCLOCK = 1
    RESET = 2
    SEND = 4
    RECALCULATE = 8
    LIVE = 16

    def __init__(self, data):
        # 2 byte header (�'SI' = 0x53,0x49)

        self.header = data[0:2]
        # 2 byte length of the complete package (16 bit, big-endian)
        self.length = data[2:4]
        # 1 byte command (1: data send to the device, 2: data received from the device)
        self.direction = data[4]
        # 1 byte flags:
        #   bit 0: set the clock (hour/minutes/seconds) in the device on upload
        #   bit 1: force reset the device (set before an update of the device)
        #   bit 2: a non-empty payload is send to the device
        #   bit 3: force recalculate the device (set on upload after changing the Sensor Offset, Outlet Height or the lookup table)
        #   bit 4: live data received from the device
        #   bit 5: n/a
        #   bit 6: n/a
        #   bit 7: n/a
        self.command = data[5]
        # 1 byte hour - used to transmit the current time to the device
        self.hour = data[6]
        # 1 byte minutes
        self.minutes = data[7]
        # 1 byte seconds
        self.seconds = data[8]
        # 2 byte eeprom start (16 bit, big-endian) - unused in live data
        self.eeprom_start = int.from_bytes(data[9:11], "big")
        # 2 byte eeprom end (16 bit, big-endian)
        self.eeprom_end = int.from_bytes(data[11:13], "big")
        # n bytes payload
        self.payload = data[13:-2]
        # 2 byte CRC16 (16 bit, big-endian)
        self.crc = data[-2:]

class EcoMeterS:
    def __init__(self, port, tank_height, offset):
        self._running = False
        self._shutdown = False
        self.deviceThread = threading.Thread(name="EcometerThread", target=EcoMeterS.monitorDevice, args=(self,))
        self.level = None
        self.usable = None
        self.total = None
        self.volume = None
        self.temperature = None
        self.distance = None
        self.percentage = None
        self.port = port
        self.offset = offset
        self.tank_height = tank_height
        self.height = self.offset + self.tank_height
        self._running = True
        self.on_data_received_callbacks = []
        self.deviceThread.start()
        return

    def add_on_data_received_callback(self, callback):
        self.on_data_received_callbacks.append(callback)

    def remove_on_data_received_callback(self, callback):
        if callback in self.on_data_received_callbacks:
            self.on_data_received_callbacks.remove(callback)


    def monitorDevice(self):
        try:
            logging.info("Entering device monitoring")
            while self._running:
                logging.debug("Reading")
                self.readData()
            logging.debug("Stopping thread")
            self._shutdown = True
        except Exception as err:
            logging.error("monitorDevice: "+str(err))

    def readData(self):
        logging.info("Connecting to device on port {:}".format(self.port))
        with serial.Serial(self.port, 115200, bytesize=8, parity='N', stopbits=1, timeout=10) as ser:
            logging.debug("Connected to device")
            data = bytearray()
            header = ser.read(2)
            logging.debug("Received data or timeout")
            if header == b'SI':
                logging.info("Received data with correct header")
                length_bytes = ser.read(2)
                length = int.from_bytes(length_bytes, "big")
                logging.debug("Receiving "+str(length)+" bytes")
                payload = ser.read(length - 4)
                logging.debug("Received whole message")
                data.extend(header)
                data.extend(length_bytes)
                data.extend(payload)
                datagram = Datagram(data)
                logging.debug("Parsed message")
                if datagram.command == Datagram.LIVE:
                    logging.info("Received live data")
                    self.registerData(datagram)
                    for callback in self.on_data_received_callbacks:
                        callback(self)
        logging.debug("Connection closed")

    def registerData(self, datagram: Datagram):
        tempF = datagram.payload[0] - 40
        self.temperature = round((tempF - 32) / 1.8, 1)
        self.distance = int.from_bytes(datagram.payload[1:3], "big")
        self.level = 190 - self.distance
        self.usable = int.from_bytes(datagram.payload[3:5], "big")
        self.total = int.from_bytes(datagram.payload[5:7], "big")
        self.updateTime = dt.datetime.now()
        self.volume = self.usable
        self.percentage = round(100.0 * self.volume / self.total, 1)

    def stop(self):
        logging.debug("Stop called")
        self._running = False
        while not self._shutdown:
            time.sleep(5)
        logging.debug("stopped")

