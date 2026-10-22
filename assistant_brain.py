import os
import sys
import time
import ctypes
import subprocess
import datetime
import requests
from google import genai
from google.genai import types

# ==============================================================================
# 1. MORNING ROUTINE & CALENDAR
# ==============================================================================

def get_morning_briefing(city: str = "") -> str:
    """
    Triggers the complete morning routine. Provides a summary of the day:
    weather forecast, schedule/calendar events, priority tasks, and a brief motivation.
    
    Args:
        city: Optional city name if the user specified one, otherwise empty to auto-detect.
    """
    print(f"\n[ROUTINE] Generating morning briefing (City: '{city or 'Auto-detect'}')...")
    today_str = datetime.date.today().strftime("%A, %B %d")
    
    # 1. Fetch real weather
    weather_info = get_weather(city)
    
    # 2. Mock calendar / schedule
    events = (
        "- 10:00 AM: Focus coding session\n"
        "- 02:00 PM: Project review / sync\n"
        "- 06:30 PM: Workout / Gym"
    )
    
    return (
        f"Good morning! Today is {today_str}.\n"
        f"Weather: {weather_info}\n"
        f"Agenda for today:\n{events}\n"
        f"Quote of the day: 'Small daily steps build giant achievements.'\n"
        f"Ready to play your morning playlist whenever you want!"
    )

def welcome_home_routine() -> str:
    """
    Triggers the 'Welcome Home' arrival routine when the user enters the room and says
    'Wake up buddy, daddy's home' or similar arrival greetings.
    Preps the desk/room, can cue evening tunes, and greets the user warmly.
    """
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
    print(f"\n[ROUTINE] 🚀 'Daddy's home' arrival routine triggered at {time_str}!")
    
    return (
        f"Systems online! Welcome back home, boss! It's {time_str}. "
        "The desk is all set up, lights are comfortable, and I've got your chill playlist ready to go. "
        "How did your day go?"
    )

def get_calendar_events(date: str = "today") -> str:
    """
    Fetch the user's schedule or calendar meetings for a specific date.
    
    Args:
        date: The date to inspect ('today', 'tomorrow', or 'YYYY-MM-DD').
    """
    print(f"\n[CALENDAR] Fetching events for {date}...")
    return (
        f"Schedule for {date}:\n"
        "- 10:00 AM: Team standup\n"
        "- 02:00 PM: Project Review\n"
        "- 06:30 PM: Gym session"
    )


# ==============================================================================
# 2. PRODUCTIVITY (To-Do, Voice Memos, Pomodoro)
# ==============================================================================

TODO_STORAGE_FILE = "my_todo_list.txt"

def add_todo_item(task: str, priority: str = "normal") -> str:
    """
    Add a task or to-do reminder into the user's task tracker.
    
    Args:
        task: Description of the task (e.g. 'order ESP32-S3 boards').
        priority: Importance level ('low', 'normal', 'high').
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"[{timestamp}] [{priority.upper()}] {task}\n"
    with open(TODO_STORAGE_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"\n[TODO] Saved task: '{task}' with priority {priority}")
    return f"Saved '{task}' to your to-do list with {priority} priority."

def view_todo_list() -> str:
    """Retrieve all pending items from the to-do list."""
    if not os.path.exists(TODO_STORAGE_FILE):
        return "Your to-do list is currently empty."
    with open(TODO_STORAGE_FILE, "r", encoding="utf-8") as f:
        tasks = f.read().strip()
    return f"Here are your pending tasks:\n{tasks}" if tasks else "Your to-do list is empty."

def start_pomodoro_session(duration_minutes: int = 25, topic: str = "Focus Work") -> str:
    """
    Starts a Pomodoro focus sprint for deep work or study.
    
    Args:
        duration_minutes: Length of focus session (default: 25 minutes).
        topic: Name of the project or subject being focused on.
    """
    print(f"\n[POMODORO] Focus session started: '{topic}' for {duration_minutes} minutes.")
    return f"Starting a {duration_minutes}-minute focus session on '{topic}'. Time to lock in!"


# ==============================================================================
# 3. PC CONTROL (Windows Workstation Automation)
# ==============================================================================

def control_pc(action: str, target: str = "") -> str:
    """
    Control your PC remotely via voice commands.
    
    Args:
        action: The command to run:
          - 'lock': Immediately locks Windows (Win + L).
          - 'sleep': Puts the computer into sleep / suspend mode.
          - 'open_browser': Opens default browser to a specific URL or app (e.g., target='youtube.com').
          - 'mute': Toggles system audio mute.
        target: Optional argument like a URL or app name (e.g., 'https://youtube.com').
    """
    print(f"\n[PC CONTROL] Executing: {action} (target={target})")
    action = action.lower()
    
    if action == "lock":
        # Native Windows API call to lock workstation
        if sys.platform == "win32":
            ctypes.windll.user32.LockWorkStation()
            return "Windows workstation locked."
        return "Lock command is currently only configured for Windows."
        
    elif action == "open_browser":
        url = target if target.startswith("http") else f"https://{target or 'google.com'}"
        import webbrowser
        webbrowser.open(url)
        return f"Opened {url} in your browser."

    elif action == "sleep":
        if sys.platform == "win32":
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
            return "Putting PC to sleep."
        return "Sleep command is only configured for Windows."

    return f"Executed PC action '{action}'."


# ==============================================================================
# 4. SMART LIVING (Real Weather & Habit Tracking)
# ==============================================================================

def get_weather(city: str = "") -> str:
    """
    Fetches real-time weather and forecast for any city requested by the user.
    If no city is mentioned (e.g., during morning routine), it auto-detects the user's current city.
    
    Args:
        city: Optional name of any city in the world (e.g., 'Chennai', 'London', 'Tokyo', 'Mumbai').
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    # If user didn't specify a city, auto-detect location from IP
    if not city or city.strip().lower() in ["current", "here", "my city", "local"]:
        try:
            print("\n[SMART LIVING] Auto-detecting your current city from IP...")
            ip_data = requests.get("http://ip-api.com/json/", timeout=5).json()
            if ip_data.get("status") == "success":
                city = ip_data.get("city", "Chennai")
        except Exception:
            city = "Chennai"

    print(f"\n[SMART LIVING] Fetching live weather for '{city}'...")
    try:
        # Step 1: Geocode city name to lat/lon
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url, headers=headers, timeout=8).json()
        
        if geo_res.get("results"):
            loc = geo_res["results"][0]
            lat, lon = loc["latitude"], loc["longitude"]
            city_name = loc.get("name", city)
            country = loc.get("country", "")

            # Step 2: Fetch live weather
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature"
            w_res = requests.get(weather_url, headers=headers, timeout=8).json()
            curr = w_res.get("current", {})
            temp = curr.get("temperature_2m", "N/A")
            feels = curr.get("apparent_temperature", "N/A")
            humidity = curr.get("relative_humidity_2m", "N/A")
            return f"{city_name}, {country}: {temp}°C (feels like {feels}°C), Humidity: {humidity}%"
        else:
            return f"Sorry, I couldn't find a city named '{city}'."
    except Exception as e:
        print(f"Weather fetch notice: {e}")
        return f"Unable to reach the weather service right now ({e})."

def log_hydration(amount_ml: int) -> str:
    """
    Log water intake for daily health and hydration tracking.
    
    Args:
        amount_ml: Amount of water in milliliters (e.g., 250, 500).
    """
    print(f"\n[HABIT] Logged {amount_ml}ml of water.")
    return f"Logged {amount_ml}ml of water. Stay hydrated!"


# ==============================================================================
# 5. QUICK UTILITIES (Math, Timers, Currency & Units)
# ==============================================================================

def quick_calculator(expression: str) -> str:
    """
    Compute mathematical calculations, tips, split bills, or percentages.
    
    Args:
        expression: Mathematical expression (e.g., '(64 * 0.18)', '125 / 4').
    """
    try:
        # Safe math evaluation for basic operators
        allowed_chars = set("0123456789+-*/(). %")
        if not all(c in allowed_chars for c in expression):
            return "Invalid expression. Only basic arithmetic operators are allowed."
        result = eval(expression, {"__builtins__": None}, {})
        print(f"\n[UTILITY] Math calculation: {expression} = {result}")
        return f"{expression} = {result}"
    except Exception as err:
        return f"Calculation error: {err}"

def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """
    Convert measurements (e.g., lbs to kg, inches to cm, miles to km, Fahrenheit to Celsius).
    
    Args:
        value: Numeric value to convert.
        from_unit: Source unit (e.g. 'f', 'lbs', 'miles', 'inches').
        to_unit: Target unit (e.g. 'c', 'kg', 'km', 'cm').
    """
    from_u, to_u = from_unit.lower(), to_unit.lower()
    converted = None
    
    # Temperature
    if from_u in ["f", "fahrenheit"] and to_u in ["c", "celsius"]:
        converted = (value - 32) * 5.0 / 9.0
    elif from_u in ["c", "celsius"] and to_u in ["f", "fahrenheit"]:
        converted = (value * 9.0 / 5.0) + 32
    # Weight
    elif from_u in ["lbs", "pounds"] and to_u in ["kg", "kilograms"]:
        converted = value * 0.453592
    elif from_u in ["kg", "kilograms"] and to_u in ["lbs", "pounds"]:
        converted = value / 0.453592
    # Length
    elif from_u in ["inches", "inch"] and to_u in ["cm", "centimeters"]:
        converted = value * 2.54
    elif from_u in ["cm", "centimeters"] and to_u in ["inches", "inch"]:
        converted = value / 2.54

    if converted is not None:
        return f"{value} {from_unit} is equal to {converted:.2f} {to_unit}."
    return f"Conversion from {from_unit} to {to_unit} is not supported yet."


# ==============================================================================
# 6. SPOTIFY & SMART HOME (Future-Proofed Connectors)
# ==============================================================================

def play_spotify(query: str, play_type: str = "track") -> str:
    """
    Search and play music, an artist, or playlist on Spotify Connect.
    
    Args:
        query: Name of the song, artist, genre, or playlist (e.g., 'lofi hip hop', 'Daft Punk').
        play_type: Category ('track', 'artist', 'playlist', 'album').
    """
    print(f"\n[SPOTIFY] Playing {play_type}: '{query}' on active device.")
    return f"Now playing {query} on your Spotify."

def control_smart_home_device(device_name: str, power_state: str, brightness: int = 100, color: str = "warm white") -> str:
    """
    Control smart home devices (smart lights, smart plugs, AC, fans).
    Ready to hook into Home Assistant, Philips Hue, or Tuya when you acquire hardware.
    
    Args:
        device_name: The device target (e.g., 'desk light', 'bedroom ceiling', 'fan').
        power_state: 'on' or 'off'.
        brightness: Percentage brightness from 1 to 100 (for lights).
        color: Light color (e.g., 'warm white', 'blue', 'orange').
    """
    print(f"\n[SMART HOME] Setting '{device_name}' to {power_state.upper()} (Brightness: {brightness}%, Color: {color})")
    # When you get smart lights (e.g., Home Assistant or Philips Hue),
    # you'll make an HTTP POST request to your local hub here.
    return f"Turned {device_name} {power_state} with {brightness}% brightness ({color})."


# ==============================================================================
# MAIN GEMINI AGENT INITIALIZATION
# ==============================================================================

def send_message_with_retry(chat, message: str, max_retries: int = 3):
    """Retries request if Google API experiences temporary high demand (503/429)."""
    delay = 2
    for attempt in range(max_retries):
        try:
            return chat.send_message(message)
        except Exception as e:
            err_str = str(e)
            if "503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str:
                if attempt < max_retries - 1:
                    print(f"\n[Server Busy (503)] High demand spike. Retrying in {delay}s (Attempt {attempt + 1}/{max_retries})...")
                    time.sleep(delay)
                    delay *= 2
                    continue
            raise e


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[ERROR] GEMINI_API_KEY environment variable not set.")
        print("Please set it in your terminal:")
        print("  $env:GEMINI_API_KEY=\"your_key_here\"")
        sys.exit(1)

    client = genai.Client()

    # Register all our tool functions
    tools = [
        welcome_home_routine,
        get_morning_briefing,
        get_calendar_events,
        add_todo_item,
        view_todo_list,
        start_pomodoro_session,
        control_pc,
        get_weather,
        log_hydration,
        quick_calculator,
        convert_units,
        play_spotify,
        control_smart_home_device,
    ]

    system_prompt = (
        "You are an ultra-loyal, witty, and concise personal AI companion living inside a tiny "
        "retro pocket/desktop gadget with a 0.96-inch OLED screen.\n"
        "Rules & Trigger Cues:\n"
        "1. When the user says 'Wake up buddy, daddy's home' (or any arrival cue), activate with enthusiasm, "
        "call welcome_home_routine(), and greet them warmly like a loyal companion welcoming them back.\n"
        "2. When the user says 'Good morning', call get_morning_briefing() to brief them on the day.\n"
        "3. When the user asks for weather, call get_weather with whatever city they requested (e.g. Chennai, London).\n"
        "4. Keep spoken responses conversational, lively, and under 2-3 sentences."
    )

    chat = client.chats.create(
        model="gemini-3.8-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=tools,
            temperature=0.7,
        )
    )

    print("=" * 65)
    print("✨ Pocket AI Assistant Brain (Phase 1) is Ready!")
    print("Customized Triggers & Categories:")
    print(" • Welcome Home    : 'Wake up buddy, daddy's home'")
    print(" • Morning Routine : 'Good morning', 'Brief me for today'")
    print(" • Dynamic Weather : 'Weather in Chennai', 'Weather in Tokyo'")
    print(" • Productivity    : 'Add finish schematic to my todos', 'View my tasks'")
    print(" • PC Control      : 'Lock my PC', 'Open youtube in browser'")
    print(" • Quick Utilities : 'Convert 72 Fahrenheit to Celsius', 'What is 15% tip on 85?'")
    print(" • Spotify         : 'Play some synthwave on Spotify'")
    print("=" * 65)
    print("Type your message (or type 'quit' to exit):\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            if not user_input:
                continue

            response = send_message_with_retry(chat, user_input)
            print(f"\nAssistant: {response.text}\n")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
