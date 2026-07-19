import urllib.request
import json
import datetime

CACHE = {}
CACHE_TTL = 600


def clima_actual(lat=37.3891, lon=-5.9845):
    now = datetime.datetime.now().timestamp()
    if "clima" in CACHE and now - CACHE["ts"] < CACHE_TTL:
        return CACHE["clima"]
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code&timezone=auto"
        req = urllib.request.Request(url, headers={"User-Agent": "MNF/1.0"})
        data = json.loads(urllib.request.urlopen(req, timeout=8).read().decode("utf-8"))
        temp = data.get("current", {}).get("temperature_2m")
        code = data.get("current", {}).get("weather_code")
        clima = {"temp": temp, "code": code, "icono": _icono(code)}
        CACHE["clima"] = clima
        CACHE["ts"] = now
        return clima
    except Exception:
        return {"temp": None, "code": None, "icono": ""}


def _icono(code):
    tabla = {
        0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
        45: "🌫️", 48: "🌫️", 51: "🌦️", 53: "🌦️", 55: "🌧️",
        61: "🌧️", 63: "🌧️", 65: "🌧️", 71: "❄️", 73: "❄️", 75: "❄️",
        80: "🌦️", 81: "🌧️", 82: "⛈️", 95: "⛈️", 96: "⛈️", 99: "⛈️",
    }
    return tabla.get(code, "🌡️")


def navbar_context(request):
    hoy = datetime.datetime.now()
    dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
             "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    fecha = f"{dias[hoy.weekday()]} {hoy.day} de {meses[hoy.month-1]} de {hoy.year}"
    hora = hoy.strftime("%H:%M")
    return {
        "hoy_fecha": fecha,
        "hoy_hora": hora,
        "clima": clima_actual(),
    }
