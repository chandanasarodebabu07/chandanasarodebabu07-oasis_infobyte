"""
assistant.py - Voice Assistant Core Logic
All the brain of the assistant - no GUI here.
Run this file directly for terminal mode.
"""

import datetime
import webbrowser
import random
import requests
import speech_recognition as sr
import pyttsx3


# ─────────────────────────────────────────────
# TTS ENGINE SETUP
# ─────────────────────────────────────────────

engine = pyttsx3.init()
voices = engine.getProperty('voices')
for v in voices:
    if 'female' in v.name.lower() or 'zira' in v.name.lower():
        engine.setProperty('voice', v.id)
        break
engine.setProperty('rate', 175)
engine.setProperty('volume', 1.0)


# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────

reminders = []

JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "What do you call a fish without eyes? A fsh!",
    "I asked my dog what 2 minus 2 is. He said nothing.",
]

GREETINGS = [
    "Hello! How can I help you today?",
    "Hi there! What can I do for you?",
    "Hey! I am here and ready to assist.",
]


# ─────────────────────────────────────────────
# CORE FUNCTIONS
# ─────────────────────────────────────────────

def speak(text):
    """Convert text to speech."""
    print(f"[Assistant]: {text}")
    engine.say(text)
    engine.runAndWait()


def listen():
    """Listen via microphone and return recognized text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n[Listening...] Speak now.")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            return ""

    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"[You]: {command}")
        return command
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that. Could you repeat?")
        return ""
    except sr.RequestError:
        speak("Speech service is unavailable. Check your internet connection.")
        return ""


def tell_time():
    return datetime.datetime.now().strftime("%I:%M %p")


def tell_date():
    return datetime.datetime.now().strftime("%A, %B %d, %Y")


def get_weather(city):
    try:
        geo = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1",
            timeout=5
        ).json()
        if not geo.get("results"):
            return f"Could not find weather for {city}."
        r = geo["results"][0]
        wx = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={r['latitude']}"
            f"&longitude={r['longitude']}&current_weather=true&temperature_unit=celsius",
            timeout=5
        ).json()
        c = wx["current_weather"]
        return f"In {r['name']}: {c['temperature']}C, wind {c['windspeed']} km/h"
    except Exception:
        return "Could not fetch weather. Check your internet."


def set_reminder(text):
    reminders.append(text)
    return f"Reminder set: '{text}'"


def list_reminders():
    if not reminders:
        return "You have no reminders set."
    return "Your reminders:\n" + "\n".join(f"- {r}" for r in reminders)


# ─────────────────────────────────────────────
# COMMAND PROCESSOR
# ─────────────────────────────────────────────

def process_command(command):
    """
    Takes a text command, returns a response string.
    Returns 'QUIT' to signal the assistant should stop.
    """
    command = command.lower().strip()
    if not command:
        return "I didn't catch that. Please try again."

    if any(w in command for w in ["exit", "quit", "bye", "goodbye", "stop"]):
        return "QUIT"

    if any(w in command for w in ["hello", "hi", "hey"]):
        return random.choice(GREETINGS)

    elif "time" in command:
        return f"The current time is {tell_time()}"

    elif "date" in command or "today" in command:
        return f"Today is {tell_date()}"

    elif "joke" in command:
        return random.choice(JOKES)

    elif "weather" in command:
        parts = command.split("in")
        city = parts[1].strip() if len(parts) > 1 else "London"
        return get_weather(city)

    elif "remind" in command:
        if "list" in command or "show" in command:
            return list_reminders()
        for phrase in ["remind me to", "remind me", "set reminder to", "set reminder"]:
            if phrase in command:
                text = command.split(phrase)[-1].strip()
                return set_reminder(text)
        return "What would you like me to remind you about?"

    elif any(w in command for w in ["search", "google", "look up"]):
        query = command.replace("search for", "").replace("google", "").replace("look up", "").strip()
        if query:
            webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            return f"Searching Google for: {query}"
        return "What would you like to search for?"

    elif "youtube" in command:
        query = command.replace("youtube", "").replace("play", "").strip()
        webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
        return f"Opening YouTube for: {query}"

    elif any(w in command for w in ["wikipedia", "who is", "what is"]):
        query = command.replace("wikipedia", "").replace("who is", "").replace("what is", "").strip()
        webbrowser.open(f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}")
        return f"Opening Wikipedia for: {query}"

    elif "help" in command:
        return (
            "I can help you with:\n"
            "- Hello / Hi\n"
            "- What time is it\n"
            "- What is today's date\n"
            "- Tell me a joke\n"
            "- Weather in [city]\n"
            "- Remind me to [task]\n"
            "- Show my reminders\n"
            "- Search for [topic]\n"
            "- YouTube [video]\n"
            "- Who is [person]\n"
            "- Goodbye"
        )

    return "I'm not sure about that. Say 'help' to see what I can do!"


# ─────────────────────────────────────────────
# TERMINAL MODE - run assistant.py directly
# ─────────────────────────────────────────────

def greet():
    hour = datetime.datetime.now().hour
    if hour < 12:
        msg = "Good morning! I am your voice assistant."
    elif hour < 18:
        msg = "Good afternoon! I am your voice assistant."
    else:
        msg = "Good evening! I am your voice assistant."
    speak(msg)


def main():
    greet()
    while True:
        command = listen()
        response = process_command(command)
        if response == "QUIT":
            speak("Goodbye! Have a great day!")
            break
        speak(response)


if __name__ == "__main__":
    main()