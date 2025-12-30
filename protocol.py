import struct
from dataclasses import dataclass

FMT = "<HffffIB"  # C struct: uint16 id, float ph, float temp, float turbidity, uint32 timestamp, uint8 redTide (19 bytes)

@dataclass
class DataPacket:
    id: int
    ph: float
    temperature: float
    turbidity: float
    timestamp: int
    redTide: int  # 0: 정상, 1: 적조 감지
    

    @staticmethod
    def decode(raw: bytes) -> "DataPacket":
        fields = struct.unpack(FMT, raw)
        return DataPacket(*fields)

    def encode(self) -> bytes:
        return struct.pack(FMT,
            self.id,
            self.ph,
            self.temperature,
            self.turbidity,
            self.timestamp,
            self.redTide
        )
