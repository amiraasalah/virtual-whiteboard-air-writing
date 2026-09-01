# 🖐️ AI Virtual Board

An interactive **AI-powered virtual whiteboard** that allows users to draw, erase, move, and interact with a digital canvas using **hand gestures** in front of a webcam.

The project combines **computer vision, hand tracking, gesture recognition, image processing, and a graphical user interface** to create a completely touch-free drawing experience.

---

## ✨ Features

### 🖐️ Real-Time Hand Tracking

The application uses a webcam to track the user's hands in real time.

It can detect and track **up to two hands simultaneously**, allowing different hands to perform different actions.

The detected hand landmarks are visualized directly on the camera feed, making the interaction easy to see and understand.

---

### ✏️ Freehand Drawing

Users can draw naturally in the air using their hand.

The index finger acts as a virtual pointer and controls the position of the brush on the digital canvas.

As the user moves their finger, the application creates a continuous drawing stroke.

This allows users to create sketches, diagrams, notes, and other freehand drawings without touching a physical surface.

---

### 📐 Geometric Shape System

The project includes a geometric-shape drawing system designed to support:

* **Straight lines**
* **Rectangles**
* **Circles**

Shapes can be previewed while the user is positioning their hand before being permanently placed on the canvas.

> **Current status:** The shape-drawing functionality is partially implemented. The shape engine and preview system exist, but gesture-based selection of the different shape modes still needs to be integrated into the main interaction system.

---

### 🧹 Gesture-Controlled Eraser

Users can erase parts of their drawing using a hand gesture instead of manually selecting an eraser.

The eraser follows the user's pointer movement and removes the selected area from the virtual canvas.

---

### ✋ Canvas Movement

The entire drawing can be moved around the workspace using a dedicated hand gesture.

This allows users to reposition their work without needing to redraw anything.

The movement system tracks the hand's displacement and translates the existing canvas accordingly.

---

### 🎨 Color Selection

The virtual board provides multiple drawing colors that can be selected directly using the hand pointer.

Currently available:

* 🔴 Red
* 🟢 Green
* 🔵 Blue

The currently selected color is displayed in the interface.

---

### 🖌️ Adjustable Brush Size

Users can control the thickness of their drawing using an on-screen brush-size slider.

The brush size can be adjusted dynamically while using the application.

The interface continuously displays the current brush size.

---

### 🗑️ Clear Canvas

The entire drawing can be cleared using the on-screen **CLEAR** control.

This provides a quick way to start a completely new drawing without restarting the application.

---

### 💾 Save Drawings

Users can save their current artwork as PNG images.

Each saved drawing receives a sequential filename, making it possible to save multiple drawings during a session.

A cooldown system prevents the same gesture from accidentally saving multiple images immediately after each other.

The application also provides visual feedback when an image is successfully saved or when the user needs to wait before saving again.

---

### 🔍 Canvas Zoom

The virtual canvas includes a zoom system that allows users to inspect their drawings at different magnifications.

The zoom level can be increased or decreased using keyboard controls.

The camera feed remains at its normal view while the canvas preview is zoomed independently.

---

### 🖥️ Fullscreen Workspace

The application runs in a fullscreen workspace designed specifically for interactive use.

The interface is divided into two main areas:

**Camera View**

Displays:

* Live webcam feed
* Hand tracking
* Hand landmarks
* Gesture interaction
* Drawing controls
* Color selection
* Brush-size controls
* Clear button
* Interaction feedback

**Virtual Canvas**

Displays the user's current drawing independently from the live camera feed.

This separation makes it easy to see both the user's gestures and the resulting artwork at the same time.

---

### 📊 Live Status Information

The application provides a top information bar showing the current state of the virtual board.

It displays:

* Current interaction mode
* Selected drawing color
* Current brush size
* Current zoom level

The mode indicator dynamically changes depending on the current interaction, such as:

* **Idle**
* **Drawing**
* **Erasing**
* **Moving**

---

### 👆 Touch-Free Interface

The project is designed around a completely touch-free interaction model.

Users can interact with the majority of the application's functionality using:

* Hand movement
* Finger positions
* Hand gestures

This removes the need for a traditional mouse or touchscreen during normal operation.

---

## 🎮 Interaction System

The application recognizes different hand configurations and converts them into actions.

The current interaction system supports gestures for:

| Interaction          | Function           |
| -------------------- | ------------------ |
| Drawing gesture      | Freehand drawing   |
| Eraser gesture       | Erasing            |
| Three-finger gesture | Moving the canvas  |
| Pointer movement     | GUI interaction    |
| Save gesture         | Saving the drawing |

The system can distinguish between the user's **left and right hands**, allowing the project to use both hands as part of its interaction system.

---

## 🖼️ Virtual Canvas

The drawing surface is maintained independently from the camera image.

This means the user's artwork remains on the virtual canvas even though the camera feed continuously changes.

The canvas supports:

* Freehand strokes
* Erasing
* Movement
* Color changes
* Brush-size changes
* Clearing
* Shape rendering
* Zoomed viewing
* Saving

---

## 🧠 Computer Vision

The project uses real-time hand landmark tracking to understand the user's movements.

Instead of requiring a trained custom gesture-classification model, the current system interprets hand gestures using the positions of detected hand landmarks.

This makes the system lightweight while still providing real-time interaction.

---

## 🖥️ Keyboard Controls

The application also provides several keyboard shortcuts:

| Key       | Function          |
| --------- | ----------------- |
| **F**     | Toggle fullscreen |
| **ESC**   | Exit fullscreen   |
| **+ / =** | Zoom in           |
| **-**     | Zoom out          |
| **Q**     | Quit application  |
| **X**     | Quit application  |

---

## 🛠️ Technologies Used

The project is built using:

* **Python** — Core application
* **OpenCV** — Computer vision, camera processing, drawing, and image manipulation
* **MediaPipe** — Real-time hand tracking and landmark detection
* **NumPy** — Virtual canvas and image operations
* **Tkinter** — Graphical user interface
* **Pillow** — Image display within the GUI

---

## 🎯 Project Goal

The goal of the AI Virtual Board is to explore how **computer vision and hand tracking can be used to create natural human-computer interactions**.

Instead of interacting with a computer through traditional input devices, the user can control a digital workspace using their hands.

The project serves as a foundation for developing more advanced gesture-controlled applications, interactive systems, and computer-vision interfaces.

---

## 🚧 Current Development Status

### Fully implemented

* ✅ Real-time webcam processing
* ✅ Two-hand detection
* ✅ Hand landmark visualization
* ✅ Finger detection
* ✅ Freehand drawing
* ✅ Gesture-controlled erasing
* ✅ Canvas movement
* ✅ Color selection
* ✅ Adjustable brush size
* ✅ Canvas clearing
* ✅ Drawing saving
* ✅ Zoom functionality
* ✅ Fullscreen interface
* ✅ Live status information
* ✅ Touch-free GUI interaction

### Partially implemented

* 🟡 Line drawing
* 🟡 Rectangle drawing
* 🟡 Circle drawing
* 🟡 Gesture-based shape selection

---

## 🚀 Future Improvements

Planned improvements include:

* 🔲 Complete gesture integration for geometric shapes
* ↩️ Undo and redo
* 🎨 Expanded color palette
* 🖌️ Multiple brush types
* 🧹 Adjustable eraser size
* 🔤 Text tool
* 📄 Multiple canvas pages
* 📑 PDF export
* 🎯 More advanced gesture recognition
* ✋ Improved gesture accuracy and smoothing
* 🤖 AI-assisted drawing
* 🎙️ Voice-controlled commands
* 👥 Collaborative virtual whiteboard
* 🎨 Advanced shape manipulation

---

## 📌 Project Status

**Active Development**

The core virtual-board experience is functional, while the geometric-shape interaction system and several advanced features are still being developed.
