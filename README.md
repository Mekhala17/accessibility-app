# accessibility-app
Web-based hand gesture and voice controlled accessibility application
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

## Preview
## 🔮 Future Enhancements

- Expand the **gesture library** to include more signs and commands.  
- Add **more voice phrases** for richer interaction.  
- Integrate with **external devices** (smart home appliances) for real-world accessibility applications.  
- Improve **accuracy and robustness** of hand gesture detection in different lighting conditions.  
- Add a **customizable user interface** for individual accessibility needs.

---

## 📜 Credits

- **Hand Gesture Recognition:** Adapted and modified from [kinivi/hand-gesture-recognition-mediapipe](https://github.com/kinivi/hand-gesture-recognition-mediapipe.git)  
- **Gesture Models:** Hand gesture and point history classifier models (`.tflite`) were trained using the kinivi repository, with modifications for this project.  
- **Voice Commands & Flask Integration:** Original work by **Mekhala Kalimuthu**

---

## 📝 License

This project is for **educational purposes**. You may adapt or extend it with **proper attribution**.

