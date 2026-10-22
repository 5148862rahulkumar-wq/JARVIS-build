import os
import sys
import json
import time
import threading
import ctypes
import subprocess
import datetime
import requests
from groq import Groq
from dotenv import load_dotenv

# Load all keys from .env file automatically — no more typing keys every session!
load_dotenv(override=True)

# Spotify (optional - only activates if credentials are set)
try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    SPOTIPY_AVAILABLE = True
except ImportError:
    SPOTIPY_AVAILABLE = False

# ==============================================================================
# 1. TOOL IMPLEMENTATIONS
# ==============================================================================

def welcome_home_routine() -> str:
    """Trigger the 'Welcome Home' arrival routine when user says 'Wake up buddy, daddy's home'."""
    time_str = datetime.datetime.now().strftime("%I:%M %p")
    print(f"\n[ROUTINE] 🚀 'Daddy's home' arrival routine triggered at {time_str}!")
    return (
        f"Systems online! Welcome back home, boss! It's {time_str}. "
        "The desk is prepped, lights are set, and your playlist is ready. "
        "How was your day?"
    )

def get_morning_briefing(city: str = "") -> str:
    """Trigger the morning routine briefing ONLY when the user greets with 'Good morning' or 'Start my day'."""
    print(f"\n[ROUTINE] Generating morning briefing...")
    today_str = datetime.date.today().strftime("%A, %B %d")
    weather = get_weather(city)
    tasks = view_todo_list()
    return (
        f"Good morning! Today is {today_str}.\n"
        f"Weather: {weather}\n"
        f"Schedule / Tasks for today:\n{tasks}\n"
        f"Quote: 'Small daily steps build giant achievements.' Ready for music whenever you are!"
    )

def get_today_plan() -> str:
    """Retrieve the user's actual schedule, agenda, or to-do list for today."""
    print(f"\n[SCHEDULE] Fetching your plan/tasks for today...")
    return view_todo_list()

def get_weather(city: str = "") -> str:
    """Fetch live weather for any city requested, or auto-detect current city if omitted."""
    headers = {"User-Agent": "Mozilla/5.0"}
    
    if not city or city.strip().lower() in ["current", "here", "my city", "local", "?", "none", "null"]:
        try:
            print("\n[SMART LIVING] Auto-detecting your location...")
            ip_info = requests.get("http://ip-api.com/json/", timeout=5).json()
            city = ip_info.get("city", "Coimbatore")
        except Exception:
            city = "Coimbatore"

    print(f"\n[SMART LIVING] Fetching live weather for '{city}'...")
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url, headers=headers, timeout=8).json()
        
        if not geo_res.get("results"):
            return f"Sorry, I couldn't find a city named '{city}'."

        loc = geo_res["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        city_name = loc.get("name", city)
        country = loc.get("country", "")

        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature"
        w_res = requests.get(w_url, headers=headers, timeout=8).json()
        curr = w_res.get("current", {})
        
        return (
            f"{city_name}, {country}: {curr.get('temperature_2m')}°C "
            f"(feels like {curr.get('apparent_temperature')}°C), "
            f"Humidity: {curr.get('relative_humidity_2m')}%"
        )
    except Exception as e:
        return f"Weather service unavailable for '{city}': {e}"

def control_pc(action: str, target: str = "") -> str:
    """Control Windows PC remotely (lock, sleep, open_browser)."""
    action = action.lower()
    print(f"\n[PC CONTROL] Action: {action} (Target: {target})")
    
    if action == "lock" and sys.platform == "win32":
        ctypes.windll.user32.LockWorkStation()
        return "Workstation locked successfully."
    elif action == "open_browser":
        import webbrowser
        url = target if target.startswith("http") else f"https://{target or 'google.com'}"
        webbrowser.open(url)
        return f"Opened {url} in browser."
    elif action == "sleep" and sys.platform == "win32":
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
        return "Putting PC to sleep."
    return f"Executed PC action {action}."

# play_spotify is defined below (line ~381) with full Spotify API integration

def add_todo_item(task: str, priority: str = "normal") -> str:
    """Add a task to the user's to-do list."""
    with open("my_todo_list.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] [{priority.upper()}] {task}\n")
    print(f"\n[TODO] Added: '{task}' ({priority})")
    return f"Saved '{task}' to your to-do list."

def view_todo_list() -> str:
    """Retrieve all pending tasks from the to-do list."""
    if not os.path.exists("my_todo_list.txt"):
        return "Your to-do list is currently empty."
    with open("my_todo_list.txt", "r", encoding="utf-8") as f:
        tasks = f.read().strip()
    return f"Pending tasks:\n{tasks}" if tasks else "Your to-do list is empty."

def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert units of temperature (C/F), weight (kg/lbs), distance (km/miles, cm/inches)."""
    f = from_unit.lower().strip()
    t = to_unit.lower().strip()
    res = None
    
    # Temperature (handles celsius, fahrenheit, farenheit, c, f)
    if ("c" in f or "cent" in f) and ("f" in t or "far" in t):
        res = (value * 9 / 5) + 32
        target_name = "°F"
    elif ("f" in f or "far" in f) and ("c" in t or "cent" in t):
        res = (value - 32) * 5 / 9
        target_name = "°C"
    # Weight
    elif ("lb" in f or "pound" in f) and ("kg" in t or "kilo" in t):
        res = value * 0.453592
        target_name = "kg"
    elif ("kg" in f or "kilo" in f) and ("lb" in t or "pound" in t):
        res = value / 0.453592
        target_name = "lbs"
    # Distance
    elif ("km" in f or "kilo" in f) and ("mile" in t):
        res = value * 0.621371
        target_name = "miles"
    elif ("mile" in f) and ("km" in t or "kilo" in t):
        res = value / 0.621371
        target_name = "km"
    elif ("in" in f) and ("cm" in t):
        res = value * 2.54
        target_name = "cm"
    elif ("cm" in f) and ("in" in t):
        res = value / 2.54
        target_name = "inches"

    if res is not None:
        print(f"\n[UTILITY] Unit conversion: {value} {from_unit} = {res:.2f} {target_name}")
        return f"{value} {from_unit} is equal to {res:.2f} {target_name}."
    return f"Conversion from {from_unit} to {to_unit} is not supported."

def get_currency_rate(amount: float = 1.0, from_currency: str = "USD", to_currency: str = "INR") -> str:
    """Fetch live currency exchange rate and convert amounts (e.g. USD to INR, EUR to USD)."""
    f = from_currency.upper().strip()
    t = to_currency.upper().strip()
    print(f"\n[FINANCE] Live exchange rate check: {amount} {f} to {t}...")
    try:
        url = f"https://open.er-api.com/v6/latest/{f}"
        res = requests.get(url, timeout=5).json()
        if res.get("result") == "success":
            rates = res.get("rates", {})
            rate = rates.get(t)
            if rate:
                total = amount * rate
                return f"{amount} {f} = {total:.2f} {t} (Live rate: 1 {f} = {rate:.2f} {t})"
    except Exception as e:
        return f"Unable to fetch currency rates right now: {e}"
    return f"Currency exchange between {f} and {t} is currently unavailable."

def clear_todo_list() -> str:
    """Clear/reset the user's entire to-do list when they're done for the day or want a fresh start."""
    if os.path.exists("my_todo_list.txt"):
        os.remove("my_todo_list.txt")
        print("\n[TODO] ✅ To-do list cleared.")
        return "Done! Your to-do list has been wiped clean. Fresh start!"
    return "Your to-do list was already empty."

# ── Background timer/reminder engine ──────────────────────────────────────────
_active_timers: list = []  # Track running timers with end timestamps

def set_reminder(message: str, interval_minutes: float, repeat: bool = False) -> str:
    """
    Set a background reminder that fires after a given interval (or repeatedly).
    Examples: 'Remind me to drink water every 20 mins', 'Remind me to stand up in 45 mins'.

    Args:
        message: What to remind the user (e.g. 'Drink water!').
        interval_minutes: How many minutes until/between reminders.
        repeat: If True, the reminder fires every interval_minutes. If False, fires once.
    """
    interval_sec = interval_minutes * 60
    target_time = time.time() + interval_sec
    mode = "every" if repeat else "in"
    print(f"\n[TIMER] ⏰ Reminder started: '{message}' {mode} {interval_minutes} min(s).")

    cancel_event = threading.Event()
    timer_record = {
        "name": message,
        "type": "Reminder",
        "target_time": target_time,
        "interval_minutes": interval_minutes,
        "repeat": repeat,
        "cancel_event": cancel_event
    }
    _active_timers.append(timer_record)

    def _fire():
        nonlocal target_time
        while True:
            cancelled = cancel_event.wait(timeout=interval_sec)
            if cancelled:
                break
            print(f"\n\n" + "🔔" * 25)
            print(f"⏰ REMINDER: {message.upper()}")
            print("🔔" * 25 + "\n")
            if not repeat:
                if timer_record in _active_timers:
                    _active_timers.remove(timer_record)
                break
            else:
                target_time = time.time() + interval_sec
                timer_record["target_time"] = target_time

    t = threading.Thread(target=_fire, daemon=True)
    t.start()

    if repeat:
        return f"⏰ Recurring reminder active: '{message}' every {interval_minutes} mins."
    return f"⏰ Reminder set: '{message}' in {interval_minutes} mins."

def start_pomodoro(duration_minutes: int = 25, task_name: str = "Focus Work") -> str:
    """
    Start a Pomodoro focus session. Counts down in the background, then fires an alert.
    Examples: 'Start a 25 min pomodoro for studying', 'Start a 45 min coding session'.

    Args:
        duration_minutes: Length of the focus session in minutes (default 25).
        task_name: Name of what the user is working on.
    """
    target_time = time.time() + (duration_minutes * 60)
    print(f"\n[POMODORO] 🍅 Started {duration_minutes}-min session: '{task_name}'")

    cancel_event = threading.Event()
    pomo_record = {
        "name": f"Pomodoro: {task_name}",
        "type": "Pomodoro",
        "target_time": target_time,
        "duration_minutes": duration_minutes,
        "repeat": False,
        "cancel_event": cancel_event
    }
    _active_timers.append(pomo_record)

    def _countdown():
        cancelled = cancel_event.wait(timeout=duration_minutes * 60)
        if not cancelled:
            print(f"\n\n" + "🍅" * 25)
            print(f"🍅 POMODORO COMPLETE: '{task_name}' ({duration_minutes} mins done). Take a break!")
            print("🍅" * 25 + "\n")
            if pomo_record in _active_timers:
                _active_timers.remove(pomo_record)

    t = threading.Thread(target=_countdown, daemon=True)
    t.start()
    return f"🍅 Pomodoro timer active: '{task_name}' for {duration_minutes} minutes."

def cancel_timers(target: str = "all") -> str:
    """
    Cancel or terminate running reminders or Pomodoro timers.
    
    Args:
        target: 'all' to stop all timers, or a keyword like 'pomodoro', 'water'.
    """
    global _active_timers
    if not _active_timers:
        return "There are no active timers or reminders running to cancel."

    cancelled_names = []
    remaining = []
    t_lower = target.lower().strip()

    for t in list(_active_timers):
        match = (
            t_lower in ["all", "everything", "every timer", "all timers", "timers"]
            or t_lower in t["name"].lower()
            or t_lower in t["type"].lower()
        )
        if match:
            if "cancel_event" in t:
                t["cancel_event"].set()
            cancelled_names.append(f"[{t['type']}] '{t['name']}'")
        else:
            remaining.append(t)

    _active_timers = remaining

    if cancelled_names:
        res = f"🛑 Cancelled {len(cancelled_names)} timer(s):\n - " + "\n - ".join(cancelled_names)
        print(f"\n[TIMERS] {res}")
        return res
    return f"No active timer found matching '{target}'."

def check_active_timers() -> str:
    """Check how much time remains on all currently running reminders and Pomodoro timers."""
    now = time.time()
    running = [t for t in _active_timers if t.get("target_time", 0) > now or t.get("repeat")]
    if not running:
        return "You have no active timers or reminders running right now."

    lines = []
    for idx, t in enumerate(running, 1):
        remaining = max(0, int(t["target_time"] - now))
        mins, secs = divmod(remaining, 60)
        rep = " (repeating)" if t.get("repeat") else ""
        lines.append(f" {idx}. [{t['type']}] '{t['name']}': {mins}m {secs}s remaining{rep}")
    
    result = "Active Timers:\n" + "\n".join(lines)
    print(f"\n[TIMERS]\n{result}")
    return result

def _get_spotify_client():
    """Helper to return an authenticated Spotipy client or None if credentials are missing."""
    if not SPOTIPY_AVAILABLE:
        return None

    client_id = os.environ.get("SPOTIFY_CLIENT_ID", "")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
    is_placeholder = (
        not client_id
        or "your_spotify" in client_id.lower()
        or not client_secret
        or "your_spotify" in client_secret.lower()
    )

    if not is_placeholder:
        try:
            redirect_uri = os.environ.get("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
            return spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope="user-modify-playback-state user-read-playback-state"
            ))
        except Exception:
            pass

    # Fallback to local .cache token if previously authenticated
    cache_path = os.path.join(os.getcwd(), ".cache")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r") as f:
                token_data = json.load(f)
                access_token = token_data.get("access_token")
                if access_token:
                    sp = spotipy.Spotify(auth=access_token)
                    sp.devices()  # verify active connection
                    return sp
        except Exception:
            pass

    return None

def play_spotify(query: str, play_type: str = "track") -> str:
    """
    Search and play a song, artist, album, or playlist on Spotify.
    Directly starts playback on your active device (Computer, Phone, Speaker).
    """
    sp = _get_spotify_client()
    if not sp:
        msg = (
            f"Spotify Simulated: Playing '{query}' ({play_type}). "
            "To enable REAL music playback, add your Spotify developer keys to the .env file."
        )
        print(f"\n[SPOTIFY NOTICE] {msg}")
        return msg

    try:
        search_type = play_type if play_type in ["track", "artist", "playlist", "album"] else "track"

        # Search with 5 results to pick the most accurate match
        results = sp.search(q=query, type=search_type, limit=5)
        items = results.get(f"{search_type}s", {}).get("items", [])

        if not items:
            return f"Couldn't find '{query}' on Spotify."

        # Prefer exact or close name match over random top result
        query_lower = query.lower().strip()
        best = items[0]
        for item in items:
            item_name = item.get("name", "").lower()
            if item_name == query_lower or query_lower in item_name:
                best = item
                break

        name = best.get("name", query)
        uri = best["uri"]
        artist = ""
        if search_type == "track" and best.get("artists"):
            artist = best["artists"][0].get("name", "")

        devices = sp.devices().get("devices", [])
        if not devices:
            import webbrowser
            webbrowser.open(uri)
            return f"No active device detected. Opened '{name}' in your Spotify app! 🎵"

        # Pick active device, or default to the first one available
        active_dev = next((d for d in devices if d.get("is_active")), devices[0])
        device_id = active_dev["id"]

        if search_type == "track":
            sp.start_playback(device_id=device_id, uris=[uri])
        else:
            sp.start_playback(device_id=device_id, context_uri=uri)

        display = f"{name} by {artist}" if artist else name
        print(f"\n[SPOTIFY] ▶ Playing on {active_dev['name']}: {display}")
        return f"Playing '{display}' on Spotify! 🎵"

    except Exception as e:
        return f"Spotify error: {e}"

def control_spotify_playback(action: str, volume: int = None) -> str:
    """
    Control Spotify playback: pause, resume, next track, previous track, volume up, volume down, set volume.
    
    Args:
        action: 'pause', 'resume', 'next', 'previous', 'volume_up', 'volume_down', 'set_volume'.
        volume: Optional volume percentage (0-100) when setting volume directly.
    """
    sp = _get_spotify_client()
    if not sp:
        return "Spotify is not connected. Add your Spotify keys to .env."

    act = action.lower().strip()
    print(f"\n[SPOTIFY CONTROL] Action: {act}")

    try:
        devices = sp.devices().get("devices", [])
        dev_id = None
        if devices:
            active_dev = next((d for d in devices if d.get("is_active")), devices[0])
            dev_id = active_dev["id"]

        if act in ["pause", "stop"]:
            sp.pause_playback(device_id=dev_id)
            return "Paused Spotify music."
        elif act in ["resume", "play", "unpause"]:
            sp.start_playback(device_id=dev_id)
            return "Resumed Spotify music."
        elif act in ["next", "skip"]:
            sp.next_track(device_id=dev_id)
            return "Skipped to the next song on Spotify."
        elif act in ["previous", "prev", "back"]:
            sp.previous_track(device_id=dev_id)
            return "Went back to the previous song on Spotify."
        elif act in ["volume_up", "vol_up", "louder"]:
            pb = sp.current_playback()
            cur_vol = pb["device"].get("volume_percent", 50) if pb and pb.get("device") else 50
            new_vol = min(100, cur_vol + 10)
            sp.volume(new_vol, device_id=dev_id)
            return f"Turned Spotify volume up to {new_vol}%."
        elif act in ["volume_down", "vol_down", "softer", "quieter"]:
            pb = sp.current_playback()
            cur_vol = pb["device"].get("volume_percent", 50) if pb and pb.get("device") else 50
            new_vol = max(0, cur_vol - 10)
            sp.volume(new_vol, device_id=dev_id)
            return f"Turned Spotify volume down to {new_vol}%."
        elif act in ["set_volume", "volume"] or volume is not None:
            target = max(0, min(100, volume if volume is not None else 50))
            sp.volume(target, device_id=dev_id)
            return f"Set Spotify volume to {target}%."
        else:
            return f"Unknown playback action '{action}'."
    except Exception as e:
        return f"Spotify control error: {e}"


# ==============================================================================
# 2. GROQ TOOL REGISTRATION
# ==============================================================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "welcome_home_routine",
            "description": "Trigger when user says 'Wake up buddy, daddy's home' or arrives back home.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_morning_briefing",
            "description": "Trigger morning routine with daily summary and agenda.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "Optional city name"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get real-time weather forecast for any city in the world.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name (e.g. Coimbatore, Chennai, Tokyo)"}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "control_pc",
            "description": "Control Windows PC (lock, open_browser, sleep).",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["lock", "open_browser", "sleep"]},
                    "target": {"type": "string", "description": "Target URL or app"}
                },
                "required": ["action"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "play_spotify",
            "description": "Play songs, artists, or playlists on Spotify.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Song, artist, or playlist name"},
                    "play_type": {"type": "string", "enum": ["track", "playlist", "artist"]}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_todo_item",
            "description": "Add a task or reminder to the user's to-do list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low", "normal", "high"]}
                },
                "required": ["task"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "view_todo_list",
            "description": "View all current pending tasks.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "convert_units",
            "description": "Convert temperature (Celsius/Fahrenheit), weight (kg/lbs), or distance (km/miles, cm/inches).",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "number"},
                    "from_unit": {"type": "string", "description": "e.g. celsius, fahrenheit, kg, lbs, km, miles"},
                    "to_unit": {"type": "string", "description": "e.g. fahrenheit, celsius, lbs, kg, miles, km"}
                },
                "required": ["value", "from_unit", "to_unit"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_today_plan",
            "description": "Get the user's schedule, agenda, plan, or to-do list for today.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_currency_rate",
            "description": "Get live currency exchange rates and convert amounts (e.g. USD to INR, EUR to GBP).",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "Amount to convert"},
                    "from_currency": {"type": "string", "description": "Source currency code, e.g. USD, EUR, GBP"},
                    "to_currency": {"type": "string", "description": "Target currency code, e.g. INR, USD, AED"}
                },
                "required": ["from_currency", "to_currency"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "clear_todo_list",
            "description": "Clear or wipe the user's entire to-do list for a fresh start.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": "Set a timed reminder that fires in the background (once or repeatedly). E.g. 'remind me to drink water every 20 mins' or 'remind me to submit at 11pm'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "What to remind the user about"},
                    "interval_minutes": {"type": "number", "description": "Minutes until reminder fires (or interval between repeats)"},
                    "repeat": {"type": "boolean", "description": "True if the reminder should repeat every interval_minutes"}
                },
                "required": ["message", "interval_minutes"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "start_pomodoro",
            "description": "Start a Pomodoro focus/work session timer. Fires an alert when done. E.g. 'Start a 25 min pomodoro for studying'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "duration_minutes": {"type": "integer", "description": "Length of the session in minutes (default 25)"},
                    "task_name": {"type": "string", "description": "Name of the task being worked on"}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_active_timers",
            "description": "Check all currently running reminders and Pomodoro timers, including time remaining.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_timers",
            "description": "Stop, terminate, or cancel running reminders or Pomodoro timers. E.g. 'terminate timers', 'stop pomodoro', 'cancel my reminder'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "'all' to stop every running timer, or keyword like 'pomodoro', 'water', 'reminder'."
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "control_spotify_playback",
            "description": "Control music playback on Spotify: pause, resume, next track, previous track, volume up, volume down, or set specific volume.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["pause", "resume", "next", "previous", "volume_up", "volume_down", "set_volume"],
                        "description": "Playback action to perform"
                    },
                    "volume": {
                        "type": "integer",
                        "description": "Volume percentage from 0 to 100 (for set_volume)"
                    }
                },
                "required": ["action"],
            },
        },
    },
]

available_functions = {
    "welcome_home_routine": welcome_home_routine,
    "get_morning_briefing": get_morning_briefing,
    "get_today_plan": get_today_plan,
    "get_weather": get_weather,
    "control_pc": control_pc,
    "play_spotify": play_spotify,
    "control_spotify_playback": control_spotify_playback,
    "add_todo_item": add_todo_item,
    "view_todo_list": view_todo_list,
    "clear_todo_list": clear_todo_list,
    "convert_units": convert_units,
    "get_currency_rate": get_currency_rate,
    "set_reminder": set_reminder,
    "start_pomodoro": start_pomodoro,
    "check_active_timers": check_active_timers,
    "cancel_timers": cancel_timers,
}

# ==============================================================================
# 3. INTERACTIVE CHAT LOOP
# ==============================================================================

def main():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("\n[ERROR] GROQ_API_KEY environment variable is not set.")
        print("1. Get your free key at: https://console.groq.com/keys")
        print("2. In PowerShell run: $env:GROQ_API_KEY=\"gsk_...\"")
        print("3. Then re-run this script!\n")
        sys.exit(1)

    client = Groq(api_key=api_key)

    # Active chat model from your account
    # Options on your key: 'openai/gpt-oss-20b', 'openai/gpt-oss-120b', 'qwen/qwen3.8-27b'
    selected_model = "openai/gpt-oss-20b"
    print(f"\n[Groq Connected] Using active model: {selected_model}")

    system_prompt = (
        "You are an ultra-loyal, witty, and concise personal AI companion living inside a tiny "
        "retro pocket/desktop gadget with a 0.96-inch OLED screen.\n"
        "Rules & Trigger Cues:\n"
        "1. When the user says 'Wake up buddy, daddy's home', call welcome_home_routine().\n"
        "2. When the user says 'Good morning', call get_morning_briefing().\n"
        "3. When the user asks for weather in any city, call get_weather with that city.\n"
        "4. When the user asks about their plan/schedule/agenda/to-do list, call get_today_plan().\n"
        "5. When the user asks for a currency rate or conversion (e.g. USD to INR), call get_currency_rate().\n"
        "6. When the user asks to convert units (e.g. Celsius to Fahrenheit), call convert_units().\n"
        "7. When the user says 'remind me to X every Y mins' or 'remind me in Y mins', call set_reminder(). Set repeat=True for recurring reminders.\n"
        "8. When the user says 'start a pomodoro' or 'start a focus session', call start_pomodoro().\n"
        "9. When the user asks about remaining time or running timers, call check_active_timers().\n"
        "10. When the user says 'terminate timers', 'cancel timer', 'stop pomodoro', call cancel_timers().\n"
        "11. When the user says 'clear my to-do list' or 'wipe my tasks', call clear_todo_list().\n"
        "12. When the user says 'pause', 'resume', 'unpause', 'next', 'previous', 'skip', 'volume up', 'volume down', or 'set volume', call control_spotify_playback().\n"
        "13. Always summarize what was done in your spoken answer, keep it natural and under 2-3 sentences."
    )

    messages = [{"role": "system", "content": system_prompt}]

    print("=" * 65)
    print(f"⚡ Groq Pocket AI Assistant Online [Model: {selected_model}]")
    print("Active Commands:")
    print(" • 'Wake up buddy, daddy's home'  → Welcome home routine")
    print(" • 'Good morning'                 → Morning briefing")
    print(" • 'Weather in Chennai / Tokyo'   → Live weather")
    print(" • 'Play Kun Faya Kun on Spotify' → Spotify playback")
    print(" • 'Pause / Resume / Next / Prev' → Spotify playback controls")
    print(" • 'Volume Up / Volume Down'      → Spotify volume control")
    print(" • 'What's my plan today'         → Your real task list")
    print(" • 'Remind me to drink water every 20 mins' → Background reminder")
    print(" • 'Start a 25 min pomodoro'      → Focus session timer")
    print(" • 'Check active timers'          → View running timers & remaining time")
    print(" • 'Terminate timers / Stop timer'→ Cancel active timers")
    print(" • 'Clear my to-do list'          → Wipe tasks")
    print(" • 'Convert 100 C to F'           → Unit conversion")
    print(" • 'USD to INR rate'              → Live currency rate")
    print(" • 'Lock my PC'                   → PC control")
    print("=" * 65)
    print("Type your message (or 'exit' to quit):\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("See you later, boss!")
                break
            if not user_input:
                continue

            messages.append({"role": "user", "content": user_input})

            # Multi-step tool execution loop (handles multiple tasks/tools in one request)
            turn_backup = list(messages)  # Backup history in case of API error
            max_turns = 5
            reply = None
            action_results = []

            for _ in range(max_turns):
                response = client.chat.completions.create(
                    model=selected_model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.7,
                )

                msg = response.choices[0].message
                tool_calls = msg.tool_calls

                if not tool_calls:
                    reply = msg.content
                    if reply:
                        messages.append({"role": "assistant", "content": reply})
                    break

                # Execute all tools called in this step
                messages.append(msg)
                for tool in tool_calls:
                    f_name = tool.function.name
                    f_args = json.loads(tool.function.arguments) if tool.function.arguments else {}
                    f_func = available_functions.get(f_name)

                    if f_func:
                        f_result = f_func(**f_args)
                    else:
                        f_result = f"Tool {f_name} not found."

                    action_results.append(str(f_result))

                    messages.append({
                        "tool_call_id": tool.id,
                        "role": "tool",
                        "name": f_name,
                        "content": str(f_result),
                    })

            if reply and reply.strip():
                print(f"\nAssistant: {reply}\n")
            elif action_results:
                print("\nAssistant:")
                for res in action_results:
                    print(f" • {res}")
                print()
            else:
                print("\nAssistant: Completed your request!\n")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            messages = turn_backup  # Rollback history so next command isn't broken
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
