import struct
from dataclasses import dataclass

FMT = "<HfffI"  # C struct: uint16 id, float temp, float turbidity, uint32 timestamp

@dataclass
class DataPacket:
    id: int
    temperature: float
    turbidity: float
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
