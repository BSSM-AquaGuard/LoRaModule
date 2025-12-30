class LoraError(Exception):
    pass

class AuxTimeoutError(LoraError):
    pass

class PacketError(LoraError):
    pass
