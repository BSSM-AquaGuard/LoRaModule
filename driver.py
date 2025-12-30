import time
import serial
import RPi.GPIO as GPIO

from .pins import LoraPins
from .enums import LoraMode
from .protocol import DataPacket
from .exceptions import AuxTimeoutError

class LoraDriver:
    def __init__(self, port: str, baudrate: int, pins: LoraPins):
        self.serial = serial.Serial(port, baudrate, timeout=1)
        self.pins = pins

        GPIO.setmode(GPIO.BCM)
        for p in (pins.m0, pins.m1, pins.aux):
            GPIO.setup(p, GPIO.OUT if p != pins.aux else GPIO.IN)

        self.set_mode(LoraMode.NORMAL)

    def wait_aux(self, timeout=1.0):
        start = time.time()
        while GPIO.input(self.pins.aux) == 0:
            if time.time() - start > timeout:
                raise AuxTimeoutError("AUX timeout")
            time.sleep(0.001)

    def set_mode(self, mode: LoraMode):
        GPIO.output(self.pins.m0, mode.value[0])
        GPIO.output(self.pins.m1, mode.value[1])
        self.wait_aux()

    def send(self, packet: DataPacket):
        self.wait_aux()
        self.serial.write(packet.encode())
        self.wait_aux()

    def receive(self) -> DataPacket | None:
        if self.serial.in_waiting >= 8:
            raw = self.serial.read(8)
            return DataPacket.decode(raw)
        return None
