from dataclasses import dataclass

@dataclass(frozen=True)
class Pinout:
    key: str
    title: str
    pins: list[str]

CATALOG = [
    Pinout("rj45", "RJ45 (8P8C)", [str(i) for i in range(1, 9)]),
    Pinout("xlr3", "XLR 3 (Audio / DMX)", ["1", "2", "3"]),
    Pinout("xlr5", "XLR 5 (DMX)", ["1", "2", "3", "4", "5"]),
]
