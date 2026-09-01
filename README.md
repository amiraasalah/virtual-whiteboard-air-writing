# 🖐️ AI Virtual Board

> An interactive **AI-powered virtual whiteboard** controlled entirely through hand gestures using a webcam.

Draw, erase, move, change colors, adjust your brush, and save your drawings — **without touching the screen.**

---

## ✨ Features

* 🖐️ **Real-time hand tracking** — Supports up to two hands
* ✏️ **Freehand drawing** — Draw naturally using your finger
* 🧹 **Gesture eraser** — Erase parts of your drawing with hand gestures
* 🎨 **Color selection** — Red, Green, and Blue
* 📏 **Adjustable brush size**
* 🖐️ **Canvas movement** — Move the virtual canvas using gestures
* 🔍 **Canvas zoom**
* 🗑️ **Clear canvas**
* 💾 **Save drawings** as PNG images
* 🖥️ **Fullscreen workspace**
* 📊 **Live status display** — Mode, color, brush size, and zoom
* 🔷 **Shape drawing system** — Lines, rectangles, and circles *(partially implemented)*
* ⌨️ **Keyboard controls**
* 🖱️ **Touch-free GUI interaction**

---

## 🛠️ Technologies

| Technology    | Purpose                   |
| ------------- | ------------------------- |
| **Python**    | Core application          |
| **OpenCV**    | Camera & image processing |
| **MediaPipe** | Hand tracking & landmarks |
| **NumPy**     | Canvas & image operations |
| **Tkinter**   | Graphical interface       |
| **Pillow**    | Image display             |

---

## 🚀 Installation

###Windows
Open PowerShell or Command Prompt.
Run the following commands:
```bash
git clone https://github.com/amiraasalah/virtual-whiteboard-air-writing.git
cd virtual-whiteboard-air-writing
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```
###Linux
Open a terminal.
Run the following commands:
```bash
git clone https://github.com/amiraasalah/virtual-whiteboard-air-writing.git
cd virtual-whiteboard-air-writing
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```


This automatically:

1. Clones the repository
2. Creates a virtual environment
3. Installs Tkinter
4. Installs the required Python packages
5. Launches the Virtual Board


> **Note:** Tkinter is normally included with Python on Windows.

---

## 🖐️ Gesture Controls

The system uses hand landmarks and finger positions to recognize different interactions.

| Gesture                 | Action                               |
| ----------------------- | ------------------------------------ |
| ☝️ Finger gesture       | Move the virtual pointer             |
| ✋ Drawing gesture       | Draw on the canvas                   |
| 👇 Erasing gesture      | Erase parts of the drawing           |
| 🤟 Three-finger gesture | Move the canvas                      |
| 🖐️ Interface gestures  | Select colors, brush size, and clear |
| 💾 Save gesture         | Save the current drawing             |

---

## 🎮 Keyboard Controls

| Key       | Action            |
| --------- | ----------------- |
| `F`       | Toggle fullscreen |
| `ESC`     | Exit fullscreen   |
| `+` / `=` | Zoom in           |
| `-`       | Zoom out          |
| `Q` / `X` | Exit application  |

---

## 📁 Project Structure

```text
virtual-board/
│
├── main.py
├── classes.py
├── requirements.txt
├── README.md
│
└── drawing*.png
```

---

## 🎨 Virtual Canvas

The application separates the **camera feed** from the **virtual drawing canvas**, allowing you to interact with the board while seeing your hand movements in real time.

The canvas supports:

* Freehand drawing
* Erasing
* Moving
* Zooming
* Color selection
* Brush-size adjustment
* Canvas clearing
* Saving drawings
* Basic geometric shapes

---

## 📊 Current Status

### ✅ Implemented

* Real-time webcam input
* Two-hand detection
* Hand landmark tracking
* Finger detection
* Freehand drawing
* Gesture erasing
* Canvas movement
* Color selection
* Brush-size control
* Canvas clearing
* PNG image saving
* Canvas zoom
* Fullscreen mode
* Live status information
* Touch-free GUI

### 🚧 Partially Implemented

* Line drawing
* Rectangle drawing
* Circle drawing
* Gesture-based shape selection

---

## 🔮 Future Improvements

* ↩️ Undo / Redo
* 🎨 More colors and brush types
* 📐 Improved shape recognition
* 🔤 Text input
* 📄 Multiple canvas pages
* 📑 PDF export
* 🤖 AI-assisted drawing
* 🎤 Voice commands
* 👥 Real-time collaboration
* ✨ Improved gesture recognition and smoothing

---

## 🎯 Project Goal

The project explores the combination of:

**Computer Vision + Hand Tracking + Gesture Recognition + Image Processing + Human-Computer Interaction**

The goal is to create a natural **touch-free digital workspace** controlled entirely through computer vision.

---

## 📄 License

This project is open-source and intended for **learning, experimentation, and further development**.
