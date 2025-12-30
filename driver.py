import time
import struct
import threading
from collections import deque
from typing import Optional
import serial
import RPi.GPIO as GPIO

from .pins import LoraPins
from .enums import LoraMode
from .protocol import DataPacket, FMT
from .exceptions import AuxTimeoutError

class LoraDriver:
    def __init__(self, port: str, baudrate: int, pins: LoraPins, buffer_size: int = 200, start_listener: bool = True):
        self.serial = serial.Serial(port, baudrate, timeout=1)
        self.pins = pins
        self._packet_size = struct.calcsize(FMT)

        GPIO.setmode(GPIO.BCM)
        for p in (pins.m0, pins.m1, pins.aux):
            GPIO.setup(p, GPIO.OUT if p != pins.aux else GPIO.IN)

        self.set_mode(LoraMode.NORMAL)

        # RX buffer & listener thread
        self._buffer = deque(maxlen=buffer_size)
        self._latest: Optional[DataPacket] = None
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        if start_listener:
            self.start_listener()

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

    def _receive_once(self) -> Optional[DataPacket]:
        if self.serial.in_waiting >= self._packet_size:
            raw = self.serial.read(self._packet_size)
            return DataPacket.decode(raw)
        return None

    def receive(self) -> DataPacket | None:
        # synchronous pull API (kept for backward compatibility)
        return self._receive_once()

    def _reader_loop(self):
        while not self._stop_event.is_set():
            pkt = self._receive_once()
            if pkt:
                self._latest = pkt
                self._buffer.append(pkt)
            else:
                time.sleep(0.01)

    def start_listener(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._thread.start()

    def stop_listener(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1)

    def latest(self) -> Optional[DataPacket]:
        return self._latest

    def buffer(self):
        return list(self._buffer)

    def close(self):
        self.stop_listener()
        self.serial.close()
