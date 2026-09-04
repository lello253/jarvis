import webbrowser
import requests
from urllib.parse import quote_plus

_DEFAULT_CITY = "San Maurizio Canavese"

def _get_live_weather(city: str) -> str | None:
    """Recupera le condizioni meteo in tempo reale usando Open-Meteo (gratuito, senza API key)."""
    try:
        # 1. Geocoding per ottenere latitudine e longitudine della città
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={quote_plus(city)}&count=1&language=it&format=json"
        geo_res = requests.get(geo_url, timeout=5).json()
        
        if not geo_res.get("results"):
            return None
            
        location = geo_res["results"][0]
        lat, lon = location["latitude"], location["longitude"]
        city_name = location.get("name", city)

        # 2. Richiesta meteo live
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&timezone=auto"
        w_res = requests.get(weather_url, timeout=5).json()
        
        current = w_res.get("current", {})
        temp = current.get("temperature_2m")
        humidity = current.get("relative_humidity_2m")
        wind = current.get("wind_speed_10m")
        code = current.get("weather_code")

        # Mappatura dei codici meteo WMO in italiano
        code_map = {
            0: "cielo sereno", 1: "prevalentemente sereno", 2: "parzialmente nuvoloso", 3: "coperto",
            45: "nebbia", 48: "nebbia con brina", 51: "pioggerella leggera", 53: "pioggerella moderata",
            61: "pioggia leggera", 63: "pioggia moderata", 65: "pioggia forte",
            71: "nevicata leggera", 73: "nevicata moderata", 75: "nevicata forte",
            80: "rovesci di pioggia", 95: "temporale"
        }
        condition = code_map.get(code, "condizioni variabili")

        return f"A {city_name} ci sono {temp}°C con {condition}. Umidità al {humidity}% e vento a {wind} km/h."
    except Exception as e:
        print(f"[Weather] ⚠️ Live weather fetch failed: {e}")
        return None


def weather_action(
    parameters: dict,
    player=None,
    session_memory=None,
) -> str:
    params = parameters or {}
    city = params.get("city")
    when = params.get("time", "oggi")
    open_browser = params.get("open_browser", False)

    if not city or not isinstance(city, str) or not city.strip():
        city = _DEFAULT_CITY

    city = city.strip()
    when = (when or "oggi").strip()

    # Tentativo di recupero meteo in tempo reale per risposte immediate
    live_report = None
    if when in ("oggi", "today", "ora", "now"):
        live_report = _get_live_weather(city)

    search_query = f"meteo {city} {when}"
    url = f"https://www.google.com/search?q={quote_plus(search_query)}"

    if open_browser:
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"[Weather] Impossibile aprire il browser: {e}")

    if live_report:
        response_msg = live_report
    else:
        response_msg = f"Meteo per {city} ({when}): ho aperto la ricerca sul browser."
        try:
            webbrowser.open(url)
        except Exception:
            pass

    _log(response_msg, player)

    if session_memory:
        try:
            session_memory.set_last_search(query=search_query, response=response_msg)
        except Exception:
            pass

    return response_msg


def _log(message: str, player=None) -> None:
    print(f"[Weather] {message}")
    if player:
        try:
            player.write_log(f"JARVIS: {message}")
        except Exception:
            pass