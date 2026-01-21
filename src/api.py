from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import time
import random

# =========================
# CONFIG (hou dit hier)
# =========================

# Kies je backend:
# - "MOCK": draait altijd, simuleert resultaten
# - "GPIO": gebruikt Raspberry Pi GPIO + CD74HC4067 (als hardware klaar is)
# - "HTTP": haalt resultaten via jouw lokale API (optioneel)
BACKEND_MODE = "MOCK"  # "MOCK" | "GPIO" | "HTTP"

# Aantal kanalen/pins dat je wilt tonen/testen (16 of 32 etc.)
PIN_COUNT = 32

# =========================
# GPIO/CD74HC4067 CONFIG
# =========================
# CD74HC4067 adresselijnen (S0..S3) en enable (EN, actief LOW)
GPIO_S0 = 5
GPIO_S1 = 6
GPIO_S2 = 13
GPIO_S3 = 19
GPIO_EN = 26

# Input pin op de Pi waar je "common" signaal binnenkomt (Z/COM)
GPIO_SIG = 21

# Debounce/settle time na kanaal-switch (sec)
MUX_SETTLE_S = 0.002

# =========================
# HTTP CONFIG (optioneel)
# =========================
HTTP_BASE_URL = "http://127.0.0.1:5000"
HTTP_TIMEOUT_S = 2.0


# =========================
# RESULT MODEL
# =========================
@dataclass
class Health:
    ok: bool
    mode: str
    detail: str = ""


# =========================
# PUBLIC API (UI gebruikt alleen dit)
# =========================
def health() -> Health:
    if BACKEND_MODE == "MOCK":
        return Health(ok=True, mode="MOCK", detail="Simulatie actief")
    if BACKEND_MODE == "GPIO":
        ok, detail = _gpio_health()
        return Health(ok=ok, mode="GPIO", detail=detail)
    if BACKEND_MODE == "HTTP":
        ok, detail = _http_health()
        return Health(ok=ok, mode="HTTP", detail=detail)
    return Health(ok=False, mode="UNKNOWN", detail=f"Onbekende BACKEND_MODE: {BACKEND_MODE}")


def run_test() -> Dict[str, str]:
    """
    Return dict: {"1":"seen"/"miss"/"unknown", ...}
    """
    if BACKEND_MODE == "MOCK":
        return _mock_test(PIN_COUNT)
    if BACKEND_MODE == "GPIO":
        return _gpio_test(PIN_COUNT)
    if BACKEND_MODE == "HTTP":
        return _http_test()
    # fallback
    return {str(i): "unknown" for i in range(1, PIN_COUNT + 1)}


# =========================
# MOCK IMPLEMENTATION
# =========================
def _mock_test(pin_count: int) -> Dict[str, str]:
    # Simuleer: meeste pins "seen", af en toe een "miss"
    out: Dict[str, str] = {}
    for i in range(1, pin_count + 1):
        r = random.random()
        if r < 0.85:
            out[str(i)] = "seen"
        elif r < 0.97:
            out[str(i)] = "miss"
        else:
            out[str(i)] = "unknown"
    return out


# =========================
# GPIO IMPLEMENTATION (CD74HC4067)
# =========================
def _gpio_health() -> Tuple[bool, str]:
    try:
        _gpio_import()
        # Als import ok is, gaan we ervan uit dat GPIO-lib aanwezig is.
        return True, "GPIO-lib OK"
    except Exception as e:
        return False, f"GPIO niet beschikbaar: {e}"


def _gpio_test(pin_count: int) -> Dict[str, str]:
    """
    Basis: selecteer kanaal op mux, lees GPIO_SIG.
    Interpretatie:
      - HIGH -> "seen"
      - LOW  -> "miss"
    """
    GPIO = _gpio_import()

    # Setup (eenmalig per run, lean maar betrouwbaar)
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    for p in (GPIO_S0, GPIO_S1, GPIO_S2, GPIO_S3, GPIO_EN):
        GPIO.setup(p, GPIO.OUT)
    GPIO.setup(GPIO_SIG, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # enable mux (active LOW)
    GPIO.output(GPIO_EN, GPIO.LOW)

    results: Dict[str, str] = {}

    # CD74HC4067 heeft 16 kanalen (0..15). Als jij 32 wil:
    # - OF je gebruikt 2 muxen,
    # - OF je test twee banken.
    # Voor nu: we mappen 1..pin_count naar kanaal (wrap modulo 16) met label.
    for pin in range(1, pin_count + 1):
        ch = (pin - 1) % 16
        _mux_select(GPIO, ch)
        time.sleep(MUX_SETTLE_S)

        val = GPIO.input(GPIO_SIG)
        results[str(pin)] = "seen" if val == 1 else "miss"

    # disable mux
    GPIO.output(GPIO_EN, GPIO.HIGH)

    # Cleanup niet verplicht, maar voorkomt “sticky state” na crashes
    GPIO.cleanup()

    return results


def _mux_select(GPIO, channel: int) -> None:
    # channel 0..15 -> bits S0..S3
    b0 = (channel >> 0) & 1
    b1 = (channel >> 1) & 1
    b2 = (channel >> 2) & 1
    b3 = (channel >> 3) & 1
    GPIO.output(GPIO_S0, b0)
    GPIO.output(GPIO_S1, b1)
    GPIO.output(GPIO_S2, b2)
    GPIO.output(GPIO_S3, b3)


def _gpio_import():
    """
    Probeer meerdere libs (afhankelijk van OS image).
    """
    try:
        import RPi.GPIO as GPIO  # type: ignore
        return GPIO
    except Exception:
        # Sommige setups gebruiken gpiozero; maar voor mux is RPi.GPIO het makkelijkst.
        # Bewust hard fail: je wil weten dat je image/lib niet klopt.
        raise


# =========================
# HTTP IMPLEMENTATION (optioneel)
# =========================
def _http_health() -> Tuple[bool, str]:
    try:
        import requests  # type: ignore
        r = requests.get(f"{HTTP_BASE_URL}/api/health", timeout=HTTP_TIMEOUT_S)
        if not r.ok:
            return False, f"HTTP {r.status_code}"
        return True, "API OK"
    except Exception as e:
        return False, str(e)


def _http_test() -> Dict[str, str]:
    """
    Verwacht een endpoint dat dict teruggeeft:
      {"1":"seen", "2":"miss", ...}
    """
    try:
        import requests  # type: ignore
        r = requests.get(f"{HTTP_BASE_URL}/api/test", timeout=HTTP_TIMEOUT_S)
        if not r.ok:
            return {str(i): "unknown" for i in range(1, PIN_COUNT + 1)}
        data = r.json()
        # normaliseer keys naar strings
        out = {}
        for k, v in data.items():
            out[str(k)] = str(v)
        return out
    except Exception:
        return {str(i): "unknown" for i in range(1, PIN_COUNT + 1)}
