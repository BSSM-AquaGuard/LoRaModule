import time
import serial

from gpiozero import DigitalOutputDevice, DigitalInputDevice

from .pins import LoRaPins
from .enums import LoraMode
from .protocol import DataPacket
from .exceptions import AuxTimeoutError


class LoraDriver:
    def __init__(self, port: str, baudrate: int, pins: LoRaPins):
        self.serial = serial.Serial(port, baudrate, timeout=1)
        self.pins = pins

        # GPIO 초기화 (BCM 번호 그대로 사용)
        self.m0 = DigitalOutputDevice(pins.m0, initial_value=False)
        self.m1 = DigitalOutputDevice(pins.m1, initial_value=False)
        self.aux = DigitalInputDevice(pins.aux)

        self.set_mode(LoraMode.NORMAL)

    def wait_aux(self, timeout: float = 1.0):
        start = time.time()
        while not self.aux.value:
            if time.time() - start > timeout:
                raise AuxTimeoutError("AUX timeout")
            time.sleep(0.001)

    def set_mode(self, mode: LoraMode):
        m0_val, m1_val = mode.value
        self.m0.value = bool(m0_val)
        self.m1.value = bool(m1_val)
        self.wait_aux()

    def send(self, packet: DataPacket):
        self.wait_aux()
        self.serial.write(packet.encode())
        self.serial.flush()
        self.wait_aux()

    def receive(self) -> DataPacket | None:
        if self.serial.in_waiting >= 8:
            raw = self.serial.read(8)
            return DataPacket.decode(raw)
        return None
