import random
from dataclasses import dataclass

@dataclass
class TestResult:
    per_pin: dict[str, str]
    passed: bool

class GpioEngine:
    def __init__(self, mock=True):
        self.mock = mock

    def run_test(self, pins: list[str]) -> TestResult:
        per = {}
        for p in pins:
            per[p] = "ok" if random.random() > 0.15 else "fail"
        return TestResult(per, all(v == "ok" for v in per.values()))
