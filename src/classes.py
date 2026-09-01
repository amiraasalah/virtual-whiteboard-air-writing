import cv2 as cv
import mediapipe as mp
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
import time

class Tracker():
    def __init__(self, break_key='q', number_of_hands=2, cam_num=0):
        self.video_capture = cv.VideoCapture(cam_num)
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=False, max_num_hands=number_of_hands)
        self.draw_method = mp.solutions.drawing_utils
        self.break_key = break_key

    def get_frame(self):
        is_read, video = self.video_capture.read()
        if not is_read:
            return None, None
        video = cv.flip(video, 1)
        RGBvideo = cv.cvtColor(video, cv.COLOR_BGR2RGB)
        results = self.hands.process(RGBvideo)
        return video, results

    def draw_landmarks(self, video, hand_landmarks):
        self.draw_method.draw_landmarks(video, hand_landmarks, self.mpHands.HAND_CONNECTIONS)
        


class control():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.last_save_time = 0
        self.save_delay = 5
        self.number_of_photos = 1

    def pointer(self, hand_landmarks):
        pointer = hand_landmarks.landmark[8]
        x = int(pointer.x * self.width)
        y = int(pointer.y * self.height)
        return x, y

    def fingers_up(self, hand_landmarks):
        tips = [8, 12, 16, 20]
        fingers = []
        for tip in tips:
            fingers.append(hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y)
        return fingers

    def thumb_down(self, hand_landmarks):
        return hand_landmarks.landmark[4].y > hand_landmarks.landmark[2].y



    def controllers(self, hand_landmarks):
        controller_1 = hand_landmarks.landmark[12]
        controller_2 = hand_landmarks.landmark[9]
        return controller_1, controller_2

    def multi_hand(self, left_hand, right_hand, tracking, painter, ui, w, h, frame):
        left_fingers = tracking.fingers_up(left_hand)
        xLeft, yLeft = tracking.pointer(left_hand)

        action = ui.handle(frame, xLeft, yLeft, painter)
        if action == "clear":
            painter.clear_all(w, h)

        if right_hand:
            

            if tracking.three_fingers_up(right_hand):
                painter.drawing = False
                painter.erasing = False
                xRight, yRight = tracking.pointer(right_hand)
                painter.start_moving(xRight, yRight)
                painter.apply_moving(xRight, yRight)
                cv.drawMarker(frame, (xRight, yRight), (255, 255, 0),
                    cv.MARKER_CROSS, 30, 2)
            elif all(left_fingers):
                painter.stop_moving()
                painter.erasing = False
                right_fingers = tracking.fingers_up(right_hand)
                xRight, yRight = tracking.pointer(right_hand)           
                c1, c2 = tracking.controllers(right_hand)
                painter.draw(xRight, yRight, c1, c2)
            elif tracking.thumb_down(left_hand):               
                painter.stop_moving()
                painter.drawing = False
                right_fingers = tracking.fingers_up(right_hand)
                xRight, yRight = tracking.pointer(right_hand)           
                c1, c2 = tracking.controllers(right_hand)
                painter.erase(xRight, yRight, c1, c2)
                cv.circle(frame, (xRight, yRight), 15, (255,255,255), 2)
            else:
                painter.drawing = False
                painter.erasing = False
                painter.stop_moving()
                painter.reset()
        else:
            painter.stop_moving()
            painter.drawing = False
            painter.erasing = False
            painter.reset()

    def submit(self, canvas, frame, hand_landmarks):
        fingers = self.fingers_up(hand_landmarks)
        height, width = frame.shape[:2]

        current_time = time.time()
        time_passed = current_time - self.last_save_time
        time_left = int(self.save_delay - time_passed)
    
        if fingers == [False, True, True, True]:

            if time_passed >= self.save_delay:
                
                name_of_photo = f"drawing{self.number_of_photos}.png"
                cv.imwrite(name_of_photo, canvas)
                self.number_of_photos += 1
                self.last_save_time = current_time

                text = "Image Saved"
                color = (0, 255, 0)

            else:
                
                text = f"Wait: {time_left}s"
                color = (0, 0, 255)

        else:
            return  

        
        font = cv.FONT_HERSHEY_SIMPLEX
        scale = 1
        thickness = 2

        (text_w, text_h), _ = cv.getTextSize(text, font, scale, thickness)
        x = (width - text_w) // 2
        y = (height + text_h) // 2

        cv.putText(frame, text, (x, y), font, scale, color, thickness)

    def three_fingers_up(self, hand_landmarks):
        tips = [12, 16, 20]
        pips = [10, 14, 18]
        three_up = all(
            hand_landmarks.landmark[t].y < hand_landmarks.landmark[p].y
            for t, p in zip(tips, pips)
        )
        index_down = hand_landmarks.landmark[8].y > hand_landmarks.landmark[6].y
        return three_up and index_down
    
    def count_fingers(self, hand_landmarks):
    
        tips = [8, 12, 16, 20]
        return sum(
        hand_landmarks.landmark[t].y < hand_landmarks.landmark[t - 2].y
        for t in tips
    )


class painting():
    def __init__(self, width, height):
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        self.prev_x = None
        self.prev_y = None
        self.color = (0, 0, 255)
        self.size = 5
        self.drawing = False
        self.erasing = False
        self.moving = False
        self.move_start_x = None
        self.move_start_y = None
        self.selection_rect = None
        self.running = True
            # In painting.__init__, add:
        self.shape_mode = None       # "line", "rect", "circle"
        self.shape_start = None      # (x, y) start point

        # ── Second Window ─────────────────────────────────────────
        self.root = tk.Tk()
        self.root.title("AI Virtual Board")
        self.root.configure(bg="#1e1e1e")
        self.root.attributes("-fullscreen", True)   
        self.is_fullscreen = True
        self.zoom = 1.0
 
        # ── Top bar ──────────────────────────────────────────────
        self.top_bar = tk.Frame(self.root, bg="#2d2d2d", height=40)
        self.top_bar.pack(fill="x", side="top")
        self.top_bar.pack_propagate(False)
 
        self.mode_label = tk.Label(
            self.top_bar, text="Mode: Idle",
            fg="white", bg="#2d2d2d", font=("Arial", 11, "bold")
        )
        self.mode_label.pack(side="left", padx=15)
 
        self.color_indicator = tk.Label(
            self.top_bar, text="      ", bg="red", width=4
        )
        self.color_indicator.pack(side="left", padx=8)
 
        self.brush_label = tk.Label(
            self.top_bar, text="Brush: --",
            fg="#aaaaaa", bg="#2d2d2d", font=("Arial", 10)
        )
        self.brush_label.pack(side="left", padx=8)
 
        self.zoom_label = tk.Label(
            self.top_bar, text="Zoom: 1.0x",
            fg="#aaaaaa", bg="#2d2d2d", font=("Arial", 10)
        )
        self.zoom_label.pack(side="left", padx=8)
 
        # ── Split layout: camera (left) | canvas (right) ─────────
        self.split_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.split_frame.pack(fill="both", expand=True)
 
        self.split_frame.columnconfigure(0, weight=1, uniform="half")
        self.split_frame.columnconfigure(2, weight=1, uniform="half")
        self.split_frame.rowconfigure(0, weight=1)
 
        # Left half — camera feed
        self.camera_label = tk.Label(self.split_frame, bg="black")
        self.camera_label.grid(row=0, column=0, sticky="nsew")
 
        # Divider
        tk.Frame(self.split_frame, bg="#444444", width=2).grid(row=0, column=1, sticky="ns")
 
        # Right half — canvas preview
        self.canvas_label = tk.Label(self.split_frame, bg="black")
        self.canvas_label.grid(row=0, column=2, sticky="nsew")
 
        self.root.focus_set()
        self.__init__bindings()
 
    def __init__bindings(self):
        self.root.bind("<f>", self.toggle_fullscreen)
        self.root.bind("<F>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)
        self.root.bind("<plus>",  lambda e: self.adjust_zoom(True))
        self.root.bind("<equal>", lambda e: self.adjust_zoom(True))
        self.root.bind("<minus>", lambda e: self.adjust_zoom(False))
        self.root.bind("<x>", lambda e: self._quit())
        self.root.bind("<X>", lambda e: self._quit())
        self.root.protocol("WM_DELETE_WINDOW", self._quit)



def draw_shape_preview(self, frame, x, y):
    """Draw a live preview ghost on the camera frame."""
    if self.shape_start is None:
        return
    sx, sy = self.shape_start
    if self.shape_mode == "line":
        cv.line(frame, (sx, sy), (x, y), self.color, self.size)
    elif self.shape_mode == "rect":
        cv.rectangle(frame, (sx, sy), (x, y), self.color, self.size)
    elif self.shape_mode == "circle":
        r = int(((x - sx)**2 + (y - sy)**2) ** 0.5)
        cv.circle(frame, (sx, sy), r, self.color, self.size)

def commit_shape(self, x, y):
    """Stamp the shape permanently onto the canvas."""
    if self.shape_start is None:
        return
    sx, sy = self.shape_start
    if self.shape_mode == "line":
        cv.line(self.canvas, (sx, sy), (x, y), self.color, self.size)
    elif self.shape_mode == "rect":
        cv.rectangle(self.canvas, (sx, sy), (x, y), self.color, self.size)
    elif self.shape_mode == "circle":
        r = int(((x - sx)**2 + (y - sy)**2) ** 0.5)
        cv.circle(self.canvas, (sx, sy), r, self.color, self.size)
    self.shape_start = None
    def _quit(self):
        self.running = False
        self.root.destroy()
 
    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        if self.is_fullscreen:
            self.root.lift()
            self.root.focus_force()
 
    def exit_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.root.attributes("-fullscreen", False)
 
    def adjust_zoom(self, increase=True):
        self.zoom = min(self.zoom + 0.1, 3.0) if increase else max(self.zoom - 0.1, 0.3)
        self.zoom_label.config(text=f"Zoom: {self.zoom:.1f}x")
 
    def update_window(self, combined_frame=None):
        # ── Right side: canvas preview with REAL Zoom ──────────────
        canvas_w = self.canvas_label.winfo_width()
        canvas_h = self.canvas_label.winfo_height()
 
        if canvas_w > 1 and canvas_h > 1:
            img = self.canvas.copy()
            h, w = img.shape[:2]

            # 1. Calculate the area to show based on Zoom level
            # If zoom is 2.0x, we only show 50% of the image (more detail)
            new_w, new_h = int(w / self.zoom), int(h / self.zoom)
            
            # 2. Get the center point to crop from
            cx, cy = w // 2, h // 2
            x1 = max(0, cx - new_w // 2)
            y1 = max(0, cy - new_h // 2)
            x2 = min(w, x1 + new_w)
            y2 = min(h, y1 + new_h)

            # 3. Crop and then resize back to fit the window split
            img_cropped = img[y1:y2, x1:x2]
            img_final = cv.resize(img_cropped, (canvas_w, canvas_h))
            
            img_final = cv.cvtColor(img_final, cv.COLOR_BGR2RGB)
            img_tk = ImageTk.PhotoImage(image=Image.fromarray(img_final))
            self.canvas_label.imgtk = img_tk
            self.canvas_label.config(image=img_tk)
 
        # ── Left side: camera feed (Fixed - No Zoom) ──────────────
        if combined_frame is not None:
            cam_w = self.camera_label.winfo_width()
            cam_h = self.camera_label.winfo_height()
            if cam_w > 1 and cam_h > 1:
                cam = cv.resize(combined_frame.copy(), (cam_w, cam_h))
                cam = cv.cvtColor(cam, cv.COLOR_BGR2RGB)
                cam_tk = ImageTk.PhotoImage(image=Image.fromarray(cam))
                self.camera_label.imgtk = cam_tk
                self.camera_label.config(image=cam_tk)
 
        # ── Top bar info ──────────────────────────────────────────
        if self.drawing:
            mode = "Drawing"
        elif self.erasing:
            mode = "Erasing"
        elif self.moving:
            mode = "Moving"
        else:
            mode = "Idle"
        self.mode_label.config(text=f"Mode: {mode}")
 
        b, g, r = self.color
        self.color_indicator.config(bg=f"#{r:02x}{g:02x}{b:02x}")
        self.brush_label.config(text=f"Brush: {self.size}px")
 
    def draw(self, x, y, c1, c2):
        if c2.y < c1.y:
            if not self.drawing or self.prev_x is None:
                self.prev_x, self.prev_y = x, y
                self.drawing = True
            cv.line(self.canvas, (self.prev_x, self.prev_y), (x, y), self.color, self.size)
            self.prev_x, self.prev_y = x, y
        else:
            self.prev_x, self.prev_y = None, None
            self.drawing = False
 
    def erase(self, x, y, c1, c2):
        if c2.y < c1.y:
            if not self.erasing or self.prev_x is None:
                self.prev_x, self.prev_y = x, y
                self.erasing = True
            cv.line(self.canvas, (self.prev_x, self.prev_y), (x, y), (0, 0, 0), 30)
            self.prev_x, self.prev_y = x, y
        else:
            self.prev_x, self.prev_y = None, None
            self.erasing = False
 
    def reset(self):
        self.prev_x, self.prev_y = None, None
        self.drawing = False
        self.erasing = False
 
    def clear_all(self, width, height):
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
 
    def start_moving(self, x, y):
        if not self.moving:
            self.move_start_x = x
            self.move_start_y = y
            self.moving = True
 
    def apply_moving(self, x, y):
        if self.moving:
            dx = x - self.move_start_x
            dy = y - self.move_start_y
            N = np.float32([[1, 0, dx], [0, 1, dy]])
            self.canvas = cv.warpAffine(self.canvas, N, (self.canvas.shape[1], self.canvas.shape[0]))
            self.move_start_x = x
            self.move_start_y = y
 
    def stop_moving(self):
        self.moving = False
        self.move_start_x = None
        self.move_start_y = None
class gui:
    def __init__(self, w, h):
        self.slider_x, self.slider_y = 50, 50
        self.slider_w, self.slider_h = 150, 20
        self.button_x1, self.button_x2 = 400, 600
        self.button_y1, self.button_y2 = 60, 110
        self.red = (0, 0, 255)
        self.green = (0, 255, 0)
        self.blue = (255, 0, 0)
        self.w = w
        self.h = h

    def click(self, px, py, x, y, w, h):
        return x < px < x + w and y < py < y + h

    def handle(self, frame, x, y, painter):
        cv.rectangle(frame, (50, 100), (100, 150), self.red, -1)
        cv.rectangle(frame, (120, 100), (170, 150), self.green, -1)
        cv.rectangle(frame, (190, 100), (240, 150), self.blue, -1)
        cv.rectangle(frame, (self.slider_x, self.slider_y), (self.slider_x + self.slider_w, self.slider_y + self.slider_h), (200, 200, 200), -1)
        handle_x = self.slider_x + int((painter.size / 20) * self.slider_w)
        cv.circle(frame, (handle_x, self.slider_y + self.slider_h // 2), 10, (0, 0, 0), -1)
        if self.click(x, y, self.slider_x, self.slider_y, self.slider_w, self.slider_h):
            rel_x = max(0, min(x - self.slider_x, self.slider_w))
            painter.size = max(1, int((rel_x / self.slider_w) * 20))
        if self.click(x, y, 50, 100, 50, 50): painter.color = self.red
        elif self.click(x, y, 120, 100, 50, 50): painter.color = self.green
        elif self.click(x, y, 190, 100, 50, 50): painter.color = self.blue
        cv.rectangle(frame, (self.button_x1, self.button_y1), (self.button_x2, self.button_y2), (0, 0, 255), 2)
        cv.putText(frame, "CLEAR", (450, 90), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        if (self.button_x1 < x < self.button_x2 and self.button_y1 < y < self.button_y2):
            return "clear"
        return None
