import webbrowser
import subprocess
import os
import time
import pyautogui
import pyperclip
from datetime import datetime
import urllib.parse
import threading

# Safe pyautogui settings
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.3

# =====================================================================
# Selenium browser driver (shared instance — one Chrome window reused)
# =====================================================================
_driver = None
_driver_lock = threading.Lock()


def _get_driver():
    """Get or create a shared Chrome driver instance."""
    global _driver
    with _driver_lock:
        if _driver is not None:
            try:
                _ = _driver.title  # check still alive
                return _driver
            except Exception:
                _driver = None

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.options import Options

            opts = Options()
            opts.add_argument("--start-maximized")
            opts.add_experimental_option("detach", True)        # browser stays open
            opts.add_experimental_option("excludeSwitches", ["enable-logging"])

            service = Service(ChromeDriverManager().install())
            _driver = webdriver.Chrome(service=service, options=opts)
            return _driver
        except Exception as e:
            print(f"[Selenium] Could not start Chrome: {e}")
            return None


def _open_url(url):
    """Open URL in the shared Selenium browser, fallback to webbrowser."""
    driver = _get_driver()
    if driver:
        driver.get(url)
    else:
        webbrowser.open(url)


def _youtube_search_and_open(query):
    """Search YouTube and click the first real video result."""
    driver = _get_driver()
    if not driver:
        webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}")
        return f"Opened YouTube search for: {query}"

    try:
        from selenium.webdriver.common.by import By

        driver.get(f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}")
        time.sleep(2.5)

        # Find first video title link (skip ads/playlists)
        deadline = time.time() + 7
        while time.time() < deadline:
            try:
                videos = driver.find_elements(By.CSS_SELECTOR, "a#video-title")
                for v in videos:
                    href = v.get_attribute("href") or ""
                    # Only real watch links, skip playlists and ads
                    if "/watch?v=" in href and v.is_displayed():
                        v.click()
                        return f"Playing first YouTube result for: {query}"
            except Exception:
                pass
            time.sleep(0.5)

        return f"Searched YouTube for {query} — could not open result"

    except Exception as e:
        print(f"[Selenium] YouTube error: {e}")
        return f"Searched YouTube for {query}"


def _google_search_and_open(query):
    """Search Google and click the first organic (non-ad) result."""
    driver = _get_driver()
    if not driver:
        webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(query)}")
        return f"Searched Google for {query}"

    try:
        from selenium.webdriver.common.by import By

        driver.get(f"https://www.google.com/search?q={urllib.parse.quote(query)}")
        time.sleep(2)

        deadline = time.time() + 7
        while time.time() < deadline:
            try:
                # Get all <a> tags inside result divs
                results = driver.find_elements(By.CSS_SELECTOR, "div.g a")
                for el in results:
                    href = el.get_attribute("href") or ""
                    # Skip Google internal, ads, tracking links
                    if (href.startswith("http")
                            and "google.com" not in href
                            and "doubleclick" not in href
                            and el.is_displayed()):
                        el.click()
                        return f"Opened first Google result for: {query}"
            except Exception:
                pass
            time.sleep(0.4)

        return f"Searched Google for {query} — could not open result"

    except Exception as e:
        print(f"[Selenium] Google error: {e}")
        return f"Searched Google for {query}"


def _youtube_pause_play():
    """Toggle play/pause on currently open YouTube video."""
    driver = _get_driver()
    if not driver:
        return "No browser open"
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys

        # Click the video player to focus it, then press K (YouTube play/pause shortcut)
        try:
            player = driver.find_element(By.CSS_SELECTOR, "video")
            player.click()
        except Exception:
            # Fallback: click the page body
            driver.find_element(By.TAG_NAME, "body").click()

        from selenium.webdriver.common.action_chains import ActionChains
        ActionChains(driver).send_keys("k").perform()
        return "Toggled play/pause"
    except Exception as e:
        print(f"[Selenium] pause/play error: {e}")
        return "Could not control YouTube"


def _youtube_next():
    """Skip to next video (Shift+N in YouTube)."""
    driver = _get_driver()
    if not driver:
        return "No browser open"
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.action_chains import ActionChains
        driver.find_element(By.TAG_NAME, "body").click()
        ActionChains(driver).key_down("\ue008").send_keys("n").key_up("\ue008").perform()  # Shift+N
        return "Skipped to next video"
    except Exception as e:
        print(f"[Selenium] next error: {e}")
        return "Could not skip video"


def _youtube_previous():
    """Restart or go to previous video (Shift+P in YouTube)."""
    driver = _get_driver()
    if not driver:
        return "No browser open"
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.action_chains import ActionChains
        driver.find_element(By.TAG_NAME, "body").click()
        ActionChains(driver).key_down("\ue008").send_keys("p").key_up("\ue008").perform()  # Shift+P
        return "Going to previous video"
    except Exception as e:
        print(f"[Selenium] previous error: {e}")
        return "Could not go to previous"


def _youtube_mute():
    """Mute/unmute YouTube video (M key)."""
    driver = _get_driver()
    if not driver:
        return "No browser open"
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.action_chains import ActionChains
        driver.find_element(By.TAG_NAME, "body").click()
        ActionChains(driver).send_keys("m").perform()
        return "Toggled mute"
    except Exception as e:
        return "Could not mute"


def _youtube_volume_up():
    """Increase YouTube volume (Up arrow x5)."""
    driver = _get_driver()
    if not driver:
        return "No browser open"
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.action_chains import ActionChains
        driver.find_element(By.TAG_NAME, "body").click()
        ac = ActionChains(driver)
        for _ in range(5):
            ac.send_keys("\ue013")   # Arrow Up
        ac.perform()
        return "Volume up"
    except Exception as e:
        return "Could not increase volume"


def _youtube_volume_down():
    """Decrease YouTube volume (Down arrow x5)."""
    driver = _get_driver()
    if not driver:
        return "No browser open"
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.action_chains import ActionChains
        driver.find_element(By.TAG_NAME, "body").click()
        ac = ActionChains(driver)
        for _ in range(5):
            ac.send_keys("\ue015")   # Arrow Down
        ac.perform()
        return "Volume down"
    except Exception as e:
        return "Could not decrease volume"


def _youtube_fullscreen():
    """Toggle fullscreen on YouTube (F key)."""
    driver = _get_driver()
    if not driver:
        return "No browser open"
    try:
        from selenium.webdriver.common.action_chains import ActionChains
        driver.find_element(By.TAG_NAME, "body").click()
        ActionChains(driver).send_keys("f").perform()
        return "Toggled fullscreen"
    except Exception as e:
        return "Could not toggle fullscreen"


def _youtube_exit():
    """Close the YouTube tab / go back to YouTube home."""
    driver = _get_driver()
    if not driver:
        return "No browser open"
    try:
        driver.get("https://www.youtube.com")
        return "Exited video, back to YouTube home"
    except Exception as e:
        print(f"[Selenium] exit error: {e}")
        return "Could not exit YouTube"




def execute_command(command):
    command_original = command
    command = command.lower().strip()

    # =====================================================================
    # SEARCH + AUTO-CLICK FIRST RESULT
    # =====================================================================

    if "search youtube for" in command:
        query = command.split("search youtube for", 1)[-1].strip()
        return _youtube_search_and_open(query) if query else "Please say what to search"

    elif "play" in command and ("on youtube" in command or "youtube" in command):
        query = command.replace("play", "").replace("on youtube", "").replace("youtube", "").strip()
        return _youtube_search_and_open(query) if query else "Please say what to play"

    # ---- YouTube controls ----
    elif any(p in command for p in ["pause youtube", "pause music", "pause video", "pause the video", "pause the music"]):
        return _youtube_pause_play()

    elif any(p in command for p in ["resume youtube", "resume music", "resume video", "play youtube", "unpause"]):
        return _youtube_pause_play()

    elif any(p in command for p in ["next video", "next song", "skip video", "skip song", "next youtube"]):
        return _youtube_next()

    elif any(p in command for p in ["previous video", "previous song", "go back video", "last video", "previous youtube"]):
        return _youtube_previous()

    elif any(p in command for p in ["mute youtube", "mute video", "mute music"]):
        return _youtube_mute()

    elif any(p in command for p in ["unmute youtube", "unmute video", "unmute music"]):
        return _youtube_mute()

    elif any(p in command for p in ["volume up youtube", "louder youtube", "increase youtube volume"]):
        return _youtube_volume_up()

    elif any(p in command for p in ["volume down youtube", "quieter youtube", "decrease youtube volume"]):
        return _youtube_volume_down()

    elif any(p in command for p in ["fullscreen youtube", "full screen youtube", "youtube fullscreen"]):
        return _youtube_fullscreen()

    elif any(p in command for p in ["exit youtube", "close youtube", "stop youtube", "exit video", "stop video", "close video"]):
        return _youtube_exit()

    elif "search google for" in command:
        query = command.split("search google for", 1)[-1].strip()
        return _google_search_and_open(query) if query else "Please say what to search"

    elif "google" in command and "search" in command:
        query = command.replace("google", "").replace("search", "").strip()
        return _google_search_and_open(query) if query else "Please say what to search"

    elif "search wikipedia for" in command:
        query = command.split("search wikipedia for", 1)[-1].strip()
        if query:
            _open_url(f"https://en.wikipedia.org/wiki/Special:Search?search={urllib.parse.quote(query)}")
            return f"Opened Wikipedia for {query}"

    elif "search amazon for" in command:
        query = command.split("search amazon for", 1)[-1].strip()
        if query:
            _open_url(f"https://www.amazon.in/s?k={urllib.parse.quote(query)}")
            return f"Searched Amazon for {query}"

    elif "navigate to" in command or "go to" in command:
        key = "navigate to" if "navigate to" in command else "go to"
        site = command.split(key, 1)[-1].strip()
        if site:
            if not site.startswith("http"):
                site = "https://" + site
            _open_url(site)
            return f"Navigating to {site}"

    # =====================================================================
    # OPEN WEBSITES
    # =====================================================================

    elif "open youtube" in command:
        _open_url("https://www.youtube.com")
        return "Opening YouTube"

    elif "open google" in command:
        _open_url("https://www.google.com")
        return "Opening Google"

    elif "open gmail" in command:
        _open_url("https://mail.google.com")
        return "Opening Gmail"

    elif "open whatsapp" in command:
        _open_url("https://web.whatsapp.com")
        return "Opening WhatsApp"

    elif "open spotify" in command:
        _open_url("https://open.spotify.com")
        return "Opening Spotify"

    elif "open maps" in command or "open google maps" in command:
        _open_url("https://maps.google.com")
        return "Opening Google Maps"

    elif "open netflix" in command:
        _open_url("https://www.netflix.com")
        return "Opening Netflix"

    elif "open twitter" in command or "open x" in command:
        _open_url("https://www.twitter.com")
        return "Opening Twitter"

    elif "open instagram" in command:
        _open_url("https://www.instagram.com")
        return "Opening Instagram"

    elif "open facebook" in command:
        _open_url("https://www.facebook.com")
        return "Opening Facebook"

    # =====================================================================
    # SYSTEM APPS
    # =====================================================================

    elif "open notepad" in command:
        subprocess.Popen(["notepad.exe"])
        return "Opening Notepad"

    elif "open calculator" in command:
        subprocess.Popen(["calc.exe"])
        return "Opening Calculator"

    elif "open paint" in command:
        subprocess.Popen(["mspaint.exe"])
        return "Opening Paint"

    elif "open file explorer" in command or "open files" in command:
        subprocess.Popen(["explorer.exe"])
        return "Opening File Explorer"

    elif "open command prompt" in command:
        subprocess.Popen("cmd.exe")
        return "Opening Command Prompt"

    elif "open settings" in command:
        subprocess.Popen(["start", "ms-settings:"], shell=True)
        return "Opening Settings"

    elif "open task manager" in command:
        subprocess.Popen(["taskmgr.exe"])
        return "Opening Task Manager"

    # =====================================================================
    # KEYBOARD SHORTCUTS
    # =====================================================================

    elif "copy" in command:
        pyautogui.hotkey("ctrl", "c")
        return "Copied"

    elif "paste" in command:
        pyautogui.hotkey("ctrl", "v")
        return "Pasted"

    elif "undo" in command:
        pyautogui.hotkey("ctrl", "z")
        return "Undo"

    elif "redo" in command:
        pyautogui.hotkey("ctrl", "y")
        return "Redo"

    elif "select all" in command:
        pyautogui.hotkey("ctrl", "a")
        return "Selected all"

    elif "save" in command:
        pyautogui.hotkey("ctrl", "s")
        return "Saved"

    elif "close tab" in command:
        pyautogui.hotkey("ctrl", "w")
        return "Closing tab"

    elif "new tab" in command:
        pyautogui.hotkey("ctrl", "t")
        return "Opening new tab"

    elif "go back" in command:
        pyautogui.hotkey("alt", "left")
        return "Going back"

    elif "go forward" in command:
        pyautogui.hotkey("alt", "right")
        return "Going forward"

    elif "refresh" in command or "reload" in command:
        pyautogui.hotkey("ctrl", "r")
        return "Refreshing"

    elif "scroll down" in command:
        pyautogui.scroll(-5)
        return "Scrolling down"

    elif "scroll up" in command:
        pyautogui.scroll(5)
        return "Scrolling up"

    elif "zoom in" in command:
        pyautogui.hotkey("ctrl", "+")
        return "Zooming in"

    elif "zoom out" in command:
        pyautogui.hotkey("ctrl", "-")
        return "Zooming out"

    elif "press enter" in command:
        pyautogui.press("enter")
        return "Pressed Enter"

    elif "press escape" in command or "press esc" in command:
        pyautogui.press("escape")
        return "Pressed Escape"

    elif "press space" in command:
        pyautogui.press("space")
        return "Pressed Space"

    elif "press tab" in command:
        pyautogui.press("tab")
        return "Pressed Tab"

    elif "take screenshot" in command:
        path = os.path.join(os.path.expanduser("~"), "Desktop",
                            f"screenshot_{datetime.now().strftime('%H%M%S')}.png")
        pyautogui.screenshot(path)
        return "Screenshot saved to Desktop"

    # =====================================================================
    # TYPE TEXT
    # =====================================================================

    elif command.startswith("type "):
        text_to_type = command_original[5:].strip()
        if text_to_type:
            pyperclip.copy(text_to_type)
            pyautogui.hotkey("ctrl", "v")
            return f"Typed: {text_to_type}"

    # =====================================================================
    # WINDOW MANAGEMENT
    # =====================================================================

    elif "minimize window" in command or "minimise window" in command:
        pyautogui.hotkey("win", "down")
        return "Window minimized"

    elif "maximize window" in command or "maximise window" in command:
        pyautogui.hotkey("win", "up")
        return "Window maximized"

    elif "close window" in command:
        pyautogui.hotkey("alt", "f4")
        return "Closing window"

    elif "switch window" in command:
        pyautogui.hotkey("alt", "tab")
        return "Switching window"

    elif "show desktop" in command:
        pyautogui.hotkey("win", "d")
        return "Showing desktop"

    # =====================================================================
    # VOLUME & MEDIA
    # =====================================================================

    elif "increase volume" in command:
        for _ in range(5):
            pyautogui.press("volumeup")
        return "Volume increased"

    elif "decrease volume" in command:
        for _ in range(5):
            pyautogui.press("volumedown")
        return "Volume decreased"

    elif "mute" in command:
        pyautogui.press("volumemute")
        return "Muted"

    elif "unmute" in command:
        pyautogui.press("volumemute")
        return "Unmuted"

    elif "next song" in command or "next track" in command:
        pyautogui.press("nexttrack")
        return "Next track"

    elif "previous song" in command or "previous track" in command:
        pyautogui.press("prevtrack")
        return "Previous track"

    # =====================================================================
    # UTILITY
    # =====================================================================

    elif "what time is it" in command or "what is the time" in command:
        now = datetime.now().strftime("%I:%M %p")
        return f"The time is {now}"

    elif "what is today" in command or "what day is it" in command:
        today = datetime.now().strftime("%A, %B %d %Y")
        return f"Today is {today}"

    elif "lock screen" in command:
        subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"])
        return "Locking screen"

    elif "exit application" in command or "close application" in command:
        pyautogui.hotkey("alt", "f4")
        return "Closing application"

    else:
        return f"Sorry, I did not understand: {command_original}"