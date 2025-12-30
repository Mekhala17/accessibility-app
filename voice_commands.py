import webbrowser
import subprocess
import os

def execute_command(command):
    command = command.lower()

    # ===================== Web Apps =====================
    if "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube"

    elif "open google" in command:
        webbrowser.open("https://www.google.com")
        return "Opening Google"

    elif "open gmail" in command:
        webbrowser.open("https://mail.google.com")
        return "Opening Gmail"

    elif "open whatsapp" in command:
        webbrowser.open("https://web.whatsapp.com")
        return "Opening WhatsApp"

    elif "open spotify" in command:
        webbrowser.open("https://open.spotify.com")
        return "Opening Spotify"

    elif "open maps" in command or "open google maps" in command:
        webbrowser.open("https://maps.google.com")
        return "Opening Google Maps"

    # ===================== System Apps (Windows) =====================
    elif "open notepad" in command:
        subprocess.Popen(["notepad.exe"])
        return "Opening Notepad"

    elif "open calculator" in command:
        subprocess.Popen(["calc.exe"])
        return "Opening Calculator"

    elif "open command prompt" in command:
        subprocess.Popen("cmd.exe")
        return "Opening Command Prompt"

    elif "open settings" in command:
        subprocess.Popen(["ms-settings:"])
        return "Opening Settings"

    # ===================== Accessibility / Help =====================
    elif "increase volume" in command:
        os.system("nircmd.exe changesysvolume 5000")
        return "Increasing volume"

    elif "decrease volume" in command:
        os.system("nircmd.exe changesysvolume -5000")
        return "Decreasing volume"

    elif "mute volume" in command:
        os.system("nircmd.exe mutesysvolume 1")
        return "Muting volume"

    # ===================== Utility Commands =====================
    elif "what time is it" in command:
        from datetime import datetime
        now = datetime.now().strftime("%I:%M %p")
        return f"The time is {now}"

    elif "exit application" in command or "close application" in command:
        return "Closing application"

    else:
        return "Sorry, command not recognized"

