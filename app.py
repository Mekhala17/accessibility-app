from flask import Flask, Response, render_template
import cv2 as cv
import copy
import time
import threading
from collections import deque, Counter
import csv
import mediapipe as mp
from gtts import gTTS
import tempfile
import os
import pygame
import numpy as np
import speech_recognition as sr

# ===================== Gesture Utils =====================
from gesture_utils import (
    pre_process_landmark,
    pre_process_point_history,
    calc_landmark_list,
    calc_bounding_rect,
    draw_bounding_rect,
    draw_info_text,
    draw_point_history,
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
        self.cap = cv.VideoCapture(self.src)
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 960)
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 540)
        self.running = True
        threading.Thread(target=self.update, daemon=True).start()

    def update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame

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
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

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
        tts = gTTS(text=text, lang="en")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            path = f.name
            tts.save(path)
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        threading.Timer(5, lambda: os.remove(path)).start()

# ===================== FPS =====================
prev_time = time.time()
fps = 0

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

@app.route("/stop_camera", methods=["POST"])
def stop_camera():
    stop_camera_safe()
    return ("", 204)

def stop_camera_safe():
    global camera_enabled
    camera_enabled = False
    camera.stop()

@app.route("/listen_voice")
def listen_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Listening")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        response = execute_command(text)
        speak(response)
    except:
        speak("Sorry, I could not understand")

    return ("", 204)

# ===================== VIDEO STREAM =====================
def generate_frames():
    global prev_time, fps, last_spoken_label

    while True:
        if not camera_enabled:
            blank = np.ones((540, 960, 3), dtype=np.uint8) * 255
            cv.putText(blank, "Camera is OFF",
                       (300, 270),
                       cv.FONT_HERSHEY_SIMPLEX,
                       1.2, (0, 0, 255), 3)
            ret, buffer = cv.imencode(".jpg", blank)
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
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

        ret, buffer = cv.imencode(".jpg", debug_image)
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

# ===================== RUN =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
