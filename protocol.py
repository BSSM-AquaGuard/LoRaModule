import struct
from dataclasses import dataclass

FMT = "<HfBB"  # ESP32 구조체랑 반드시 동일

@dataclass
class DataPacket:
    id: int
    temperature: float
    turbidity: int
    timestamp: int

    @staticmethod
    def decode(raw: bytes) -> "DataPacket":
        fields = struct.unpack(FMT, raw)
        return DataPacket(*fields)

    def encode(self) -> bytes:
        return struct.pack(FMT,
            self.id,
            self.temperature,
            self.turbidity,
            self.timestamp
        )
