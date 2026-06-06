# Accessibility App

A **hand gesture and voice-controlled application** built using **Python**, **Flask**, and **MediaPipe**.  
This project allows users to interact with their computer through **hand gestures** and **voice commands**.

> **Note:** The hand gesture recognition part is **adapted and modified** from [kinivi/hand-gesture-recognition-mediapipe](https://github.com/kinivi/hand-gesture-recognition-mediapipe.git).  
> All other functionality, including the Flask app, voice command integration, and UI, are **original contributions**.

---

## Purpose & Target Users

This is a **prototype** designed to help people who are **blind, deaf, or mute**:

- **Blind users (`:eyes:`)**: Voice commands and audio feedback allow interaction without relying on vision.  
- **Deaf users (`:ear:`)**: Hand gesture recognition provides a visual interface for control.  
- **Mute users (`:mute:`)**: Hand gestures allow communication and command execution without speaking.  

By combining **voice and gesture interfaces**, the app creates an **inclusive, multi-modal interaction system**.

---

## Features

- **Real-time Hand Gesture Recognition** using MediaPipe and custom classifiers (adapted and modified from [kinivi/hand-gesture-recognition-mediapipe](https://github.com/kinivi/hand-gesture-recognition-mediapipe.git)).  
- **Voice Command Integration** using Google Speech Recognition and gTTS.  
- **Web Interface** built with Flask:
  - `/hand` – Hand gesture interface.  
  - `/voice` – Voice command interface.  
- **Audio Feedback** for detected gestures and executed commands.  
- **Custom Gesture Models** for hand signs and point history.

---

## Feature Benefits for Users

| Feature                    | Blind (`:eyes:`) | Deaf (`:ear:`) | Mute (`:mute:`) |
|----------------------------|----------------|----------------|----------------|
| Hand Gesture Recognition    | ❌             | ✅ Visual control | ✅ Execute commands |
| Voice Command Recognition   | ✅ Audio feedback | ❌               | ❌               |
| Audio Feedback              | ✅ Confirmation  | ❌               | ❌               |
| Web Interface               | ✅ Navigate     | ✅ Visual control | ✅ Navigate      |

---

## Key Files / Folders

- `app.py` – Main Flask application  
- `voice_commands.py` – Voice command logic  
- `gesture_utils.py` – Gesture processing utilities  
- `model/` – Gesture model files (`.tflite` and labels)  
- `templates/` – HTML files for Flask pages  
- `static/` – CSS, JS, and media assets  

---

## 🔮 Future Enhancements

- Expand the **gesture library** to include more signs and commands.  
- Add **more voice phrases** for richer interaction.  
- Integrate with **external devices** (smart home appliances) for real-world accessibility applications.  
- Improve **accuracy and robustness** of hand gesture detection in different lighting conditions.  
- Add a **customizable user interface** for individual accessibility needs.

---
## 🎬 Demo

[![Watch the Demo](https://img.youtube.com/vi/aQF05q1Ozj0/0.jpg)](https://youtu.be/aQF05q1Ozj0)

<img width="20" height="10" alt="WhatsApp Image 2026-06-06 at 1 19 51 PM" src="https://github.com/user-attachments/assets/3c0b2541-a8e8-4cb7-848b-0bd95ca0b5cd" />
<img width="1600" height="940" alt="image" src="https://github.com/user-attachments/assets/11a88c41-3eef-4009-894b-c73cd18fd276" />
<img width="1600" height="940" alt="image" src="https://github.com/user-attachments/assets/d19b24ff-8ede-4c6a-a963-eb565cc5b837" />
<img width="1600" height="885" alt="image" src="https://github.com/user-attachments/assets/c6cebe6b-64f4-4430-97a5-47577908298e" />
<img width="1080" height="539" alt="image" src="https://github.com/user-attachments/assets/df6858fa-4a8a-41ca-861b-8184a969382d" />






## 📜 Credits

- **Hand Gesture Recognition:** Adapted and modified from [kinivi/hand-gesture-recognition-mediapipe](https://github.com/kinivi/hand-gesture-recognition-mediapipe.git)  
- **Gesture Models:** Hand gesture and point history classifier models (`.tflite`) were trained using the kinivi repository, with modifications for this project.  
- **Voice Commands & Flask Integration:** Original work by **Mekhala Kalimuthu**

---

## 📝 License

This project is for **educational purposes**. You may adapt or extend it with **proper attribution**.

