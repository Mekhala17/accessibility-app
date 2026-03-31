from flask import Flask, Response, render_template, request, jsonify
import cv2 as cv
import copy
import time
import threading
from collections import deque, Counter
import csv
import numpy as np
from gtts import gTTS
import tempfile
import os
import pygame
import speech_recognition as sr
import pyautogui
import mediapipe as mp

print("Starting app initialization...")

# ===================== Gesture Utils =====================
from gesture_utils import (
    pre_process_landmark,
    calc_landmark_list,
    calc_bounding_rect,
    draw_bounding_rect,
    draw_info_text,
    draw_info
)

from model.keypoint_classifier.keypoint_classifier import KeyPointClassifier
from model.point_history_classifier.point_history_classifier import PointHistoryClassifier
from voice_commands import execute_command

# ===================== Flask =====================
app = Flask(__name__)

# ===================== Camera State =====================
camera_enabled = False


# ===================== Camera Class =====================
class Camera:
    def __init__(self, src=0):
        self.src = src
        self.cap = None
        self.frame = None
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        if self.running:
            return
        try:
            self.cap = cv.VideoCapture(self.src)
            if not self.cap.isOpened():
                print("ERROR: Could not open camera!")
                return False

            self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 960)
            self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 540)

            self.running = True
            threading.Thread(target=self.update, daemon=True).start()
            print("Camera started successfully")
            return True
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False

    def update(self):
        while self.running:
            try:
                ret, frame = self.cap.read()
                if ret:
                    with self.lock:
                        self.frame = frame
            except Exception as e:
                print(f"Error in camera update: {e}")
            time.sleep(0.01)

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.frame = None

    def get_frame(self):
        with self.lock:
            return None if self.frame is None else self.frame.copy()


camera = Camera()

# ===================== Models =====================
print("Loading hand gesture models...")
keypoint_classifier = KeyPointClassifier(
    "model/keypoint_classifier/keypoint_classifier.tflite"
)
point_history_classifier = PointHistoryClassifier(
    "model/point_history_classifier/point_history_classifier.tflite"
)

# ===================== Labels =====================
with open("model/keypoint_classifier/keypoint_classifier_label.csv", encoding="utf-8-sig") as f:
    keypoint_classifier_labels = [row[0] for row in csv.reader(f)]

# ===================== MediaPipe =====================
print("Initializing MediaPipe...")
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# MediaPipe FaceMesh with refine_landmarks (this is key!)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    refine_landmarks=True,  # THIS ENABLES IRIS TRACKING!
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Screen size
screen_w, screen_h = pyautogui.size()
pyautogui.FAILSAFE = False

# ===================== Eye Gaze State =====================
eye_gaze_enabled = False
eye_prev_x = 0
eye_prev_y = 0
eye_smoothening = 5
blink_cooldown = 0

# ===================== Gesture History =====================
history_length = 16
point_history = deque(maxlen=history_length)
sign_history = deque(maxlen=10)
last_spoken_label = None

# ===================== Audio =====================
pygame.mixer.init()
audio_lock = threading.Lock()


def speak(text):
    with audio_lock:
        try:
            tts = gTTS(text=text, lang="en")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                path = f.name
                tts.save(path)
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            try:
                os.remove(path)
            except:
                pass
        except Exception as e:
            print(f"Error in speak: {e}")


# ===================== FPS =====================
prev_time = time.time()
fps = 0

print("App initialization complete!")


# ===================== ROUTES =====================
@app.route("/")
def welcome():
    stop_camera_safe()
    return render_template("welcome.html")


@app.route("/hand")
def hand_page():
    global camera_enabled
    camera_enabled = True
    camera.start()
    return render_template("hand.html")


@app.route("/voice")
def voice_page():
    stop_camera_safe()
    return render_template("voice.html")


@app.route("/eye")
def eye_page():
    global camera_enabled, eye_gaze_enabled
    camera_enabled = True
    eye_gaze_enabled = False
    camera.start()
    return render_template("eye.html")


@app.route("/stop_camera", methods=["POST"])
def stop_camera():
    stop_camera_safe()
    return ("", 204)


@app.route("/toggle_eye_gaze", methods=["POST"])
def toggle_eye_gaze():
    global eye_gaze_enabled, eye_smoothening
    data = request.get_json()
    eye_gaze_enabled = data.get("enabled", False)
    if "smoothing" in data:
        eye_smoothening = max(1, int(data["smoothing"]))
    print(f"Eye gaze enabled: {eye_gaze_enabled}, smoothing: {eye_smoothening}")
    return jsonify({"eye_gaze_enabled": eye_gaze_enabled, "smoothing": eye_smoothening})


def stop_camera_safe():
    global camera_enabled, eye_gaze_enabled
    camera_enabled = False
    eye_gaze_enabled = False
    camera.stop()


@app.route("/speak", methods=["POST"])
def speak_text():
    """Text-to-speech for AAC board"""
    data = request.get_json()
    text = data.get("text", "")
    if text:
        threading.Thread(target=speak, args=(text,), daemon=True).start()
    return ("", 204)


@app.route("/listen_voice")
def listen_voice():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            speak("Listening")
            audio = recognizer.listen(source, timeout=5)
        try:
            text = recognizer.recognize_google(audio)
            response = execute_command(text)
            speak(response)
        except sr.UnknownValueError:
            speak("Sorry, I could not understand")
        except sr.RequestError:
            speak("Sorry, there was an error with the speech service")
    except Exception as e:
        print(f"Error in listen_voice: {e}")
        speak("Sorry, there was an error")
    return ("", 204)


@app.route("/listen_voice_json")
def listen_voice_json():
    """Listen once, execute command, speak response, then return JSON.
    Because we WAIT for speak() to finish before returning,
    the mic won't reopen until the assistant has finished talking."""
    recognizer = sr.Recognizer()
    heard    = ""
    response = ""
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=8)

        heard    = recognizer.recognize_google(audio)
        response = execute_command(heard)

        # Speak SYNCHRONOUSLY — blocks until done, so mic stays closed
        speak(response)

    except sr.WaitTimeoutError:
        heard    = ""
        response = "No speech detected"
    except sr.UnknownValueError:
        heard    = ""
        response = "Could not understand"
    except sr.RequestError as e:
        heard    = ""
        response = f"Speech service error"
    except Exception as e:
        print(f"listen_voice_json error: {e}")
        heard    = ""
        response = "An error occurred"

    return jsonify({"heard": heard, "response": response})


@app.route("/current_sign")
def current_sign():
    if sign_history:
        most_common_id = Counter(sign_history).most_common(1)[0][0]
        label = keypoint_classifier_labels[most_common_id]
    else:
        label = "—"
    return jsonify({"sign": label})


# ===================== VIDEO STREAM — Hand Signs =====================
def generate_frames():
    global prev_time, fps, last_spoken_label

    while True:
        if not camera_enabled:
            blank = np.ones((540, 960, 3), dtype=np.uint8) * 255
            cv.putText(blank, "Camera is OFF", (300, 270),
                       cv.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            _, buf = cv.imencode(".jpg", blank)
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
            time.sleep(0.1)
            continue

        frame = camera.get_frame()
        if frame is None:
            time.sleep(0.05)
            continue

        frame = cv.flip(frame, 1)
        debug_image = copy.deepcopy(frame)

        current_time = time.time()
        fps = 0.9 * fps + 0.1 * (1 / max(current_time - prev_time, 1e-6))
        prev_time = current_time

        image_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(
                    results.multi_hand_landmarks,
                    results.multi_handedness
            ):
                brect = calc_bounding_rect(debug_image, hand_landmarks)
                landmark_list = calc_landmark_list(debug_image, hand_landmarks)
                pre_landmarks = pre_process_landmark(landmark_list)
                hand_sign_id = keypoint_classifier(pre_landmarks)

                sign_history.append(hand_sign_id)
                most_common_id, count = Counter(sign_history).most_common(1)[0]

                if count == len(sign_history):
                    label = keypoint_classifier_labels[most_common_id]
                    if label != last_spoken_label:
                        threading.Thread(target=speak, args=(label,), daemon=True).start()
                        last_spoken_label = label

                debug_image = draw_bounding_rect(True, debug_image, brect)
                debug_image = draw_info_text(
                    debug_image, brect, handedness,
                    keypoint_classifier_labels[hand_sign_id]
                )
        else:
            sign_history.clear()

        debug_image = draw_info(debug_image, fps, 0, -1)
        _, buf = cv.imencode(".jpg", debug_image)
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"


# ===================== VIDEO STREAM — Eye Gaze (PROVEN LOGIC) =====================
def generate_eye_frames():
    global eye_prev_x, eye_prev_y, eye_smoothening, blink_cooldown

    while True:
        if not camera_enabled:
            blank = np.ones((540, 960, 3), dtype=np.uint8) * 20
            cv.putText(blank, "Camera is OFF", (300, 270),
                       cv.FONT_HERSHEY_SIMPLEX, 1.2, (0, 100, 255), 3)
            _, buf = cv.imencode(".jpg", blank)
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
            time.sleep(0.1)
            continue

        frame = camera.get_frame()
        if frame is None:
            time.sleep(0.05)
            continue

        frame = cv.flip(frame, 1)
        frame_h, frame_w, _ = frame.shape
        debug_image = copy.deepcopy(frame)

        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        output = face_mesh.process(rgb_frame)

        landmark_points = output.multi_face_landmarks
        status_text = "No face detected"
        status_color = (0, 80, 255)

        if landmark_points:
            landmarks = landmark_points[0].landmark

            try:
                # -------- Eye gaze (cursor movement) using iris landmarks 474-477 --------
                iris_landmarks = landmarks[474:478]

                for id, landmark in enumerate(iris_landmarks):
                    x = int(landmark.x * frame_w)
                    y = int(landmark.y * frame_h)
                    cv.circle(debug_image, (x, y), 3, (0, 255, 0), -1)

                    # Use iris landmark 1 (right iris center) for cursor control
                    if id == 1:
                        screen_x = screen_w * landmark.x
                        screen_y = screen_h * landmark.y

                        # Cursor smoothing
                        curr_x = eye_prev_x + (screen_x - eye_prev_x) / eye_smoothening
                        curr_y = eye_prev_y + (screen_y - eye_prev_y) / eye_smoothening

                        if eye_gaze_enabled:
                            pyautogui.moveTo(curr_x, curr_y)

                        eye_prev_x, eye_prev_y = curr_x, curr_y

                # -------- Blink detection (left eye) using eyelid landmarks --------
                left_eyelids = [landmarks[145], landmarks[159]]

                for landmark in left_eyelids:
                    x = int(landmark.x * frame_w)
                    y = int(landmark.y * frame_h)
                    cv.circle(debug_image, (x, y), 3, (0, 255, 255), -1)

                blink_distance = abs(left_eyelids[0].y - left_eyelids[1].y)

                if blink_distance < 0.01:
                    cv.putText(debug_image, "BLINK - CLICK!", (50, 80),
                               cv.FONT_HERSHEY_DUPLEX, 1.8, (0, 255, 0), 3)

                    if blink_cooldown <= 0 and eye_gaze_enabled:
                        pyautogui.click()
                        blink_cooldown = 30  # Cooldown to prevent multiple clicks
                        status_text = "✓ CLICKED!"
                        status_color = (0, 255, 0)
                    else:
                        status_text = "✓ Eyes tracking + Blink detected"
                        status_color = (0, 255, 150)
                else:
                    if eye_gaze_enabled:
                        status_text = "✓ Right iris tracking cursor"
                        status_color = (0, 255, 150)
                    else:
                        status_text = "✓ Face detected | Control OFF"
                        status_color = (100, 200, 150)

                if blink_cooldown > 0:
                    blink_cooldown -= 1

            except Exception as e:
                print(f"Error processing landmarks: {e}")
                status_text = "Error processing face"
                status_color = (0, 0, 255)

        # Status bar
        overlay = debug_image.copy()
        cv.rectangle(overlay, (0, 0), (frame_w, 44), (10, 10, 30), -1)
        cv.addWeighted(overlay, 0.65, debug_image, 0.35, 0, debug_image)
        gaze_label = "ON" if eye_gaze_enabled else "OFF"
        cv.putText(debug_image,
                   f"Eye Control: {gaze_label}  |  {status_text}",
                   (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

        _, buf = cv.imencode(".jpg", debug_image)
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"


# ===================== VIDEO FEED ROUTES =====================
@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/eye_feed")
def eye_feed():
    return Response(generate_eye_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


# ===================== RUN =====================
if __name__ == "__main__":
    try:
        print("Starting Flask server on 0.0.0.0:5000")
        app.run(host="0.0.0.0", port=5001, debug=False, threaded=True)
    except Exception as e:
        print(f"Error starting app: {e}")