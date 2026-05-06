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
            fingers.append(
                hand_landmarks.landmark[tip].y <
                hand_landmarks.landmark[tip - 2].y
            )

        return fingers

    def thumb_down(self, hand_landmarks):
        return hand_landmarks.landmark[4].y > hand_landmarks.landmark[2].y

    def controllers(self, hand_landmarks):
        controller_1 = hand_landmarks.landmark[12]
        controller_2 = hand_landmarks.landmark[9]
        return controller_1, controller_2

    def multi_hand(self, left_hand, right_hand, tracking, painter, ui, w, h, frame):
        xLeft, yLeft = tracking.pointer(left_hand)
        left_fingers = tracking.fingers_up(left_hand)

        # Handle UI interaction (Buttons/Modes)
        action = ui.handle(frame, xLeft, yLeft, painter)

        if action == "clear":
            painter.clear_all(w, h)

        if ui.mode == "drawing":

            # --- NORMAL DRAWING MODE LOGIC ---[cite: 1]
            if right_hand:

                if tracking.three_fingers_up(right_hand):
                    painter.drawing = False
                    painter.erasing = False

                    xRight, yRight = tracking.pointer(right_hand)
                    painter.start_moving(xRight, yRight)
                    painter.apply_moving(xRight, yRight)

                    cv.drawMarker(
                        frame,
                        (xRight, yRight),
                        (255, 255, 0),
                        cv.MARKER_CROSS,
                        30,
                        2
                    )

                elif all(left_fingers):
                    painter.stop_moving()
                    painter.erasing = False

                    xRight, yRight = tracking.pointer(right_hand)
                    c1, c2 = tracking.controllers(right_hand)

                    painter.draw(xRight, yRight, c1, c2)

                elif tracking.thumb_down(left_hand):
                    painter.stop_moving()
                    painter.drawing = False

                    xRight, yRight = tracking.pointer(right_hand)
                    c1, c2 = tracking.controllers(right_hand)

                    painter.erase(xRight, yRight, c1, c2)

                    cv.circle(frame, (xRight, yRight), 15, (255, 255, 255), 2)

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

        elif ui.mode == "shapes":

            # --- SHAPES MODE LOGIC ---[cite: 1]
            painter.stop_moving()
            painter.reset()

            if right_hand and painter.active_shape:

                l_idx = tracking.pointer(left_hand)

                l_thm = (
                    int(left_hand.landmark[4].x * w),
                    int(left_hand.landmark[4].y * h)
                )

                r_idx = (
                    int(right_hand.landmark[8].x * w),
                    int(right_hand.landmark[8].y * h)
                )

                r_thm = (
                    int(right_hand.landmark[4].x * w),
                    int(right_hand.landmark[4].y * h)
                )

                right_middle_up = right_hand.landmark[12].y < right_hand.landmark[10].y

                if painter.active_shape == "rect":
                    painter.draw_shape_preview(frame, l_idx, r_idx)

                    if right_middle_up:
                        painter.commit_shape(l_idx, r_idx)

                elif painter.active_shape == "tri":
                    painter.draw_shape_preview(frame, l_idx, r_idx, l_thm)

                    if right_middle_up:
                        painter.commit_shape(l_idx, r_idx, l_thm)

                elif painter.active_shape == "circle":
                    painter.draw_shape_preview(frame, l_idx, r_idx)

                    if right_middle_up:
                        painter.commit_shape(l_idx, r_idx)

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
                text, color = "Image Saved", (0, 255, 0)

            else:
                text, color = f"Wait: {time_left}s", (0, 0, 255)

            font = cv.FONT_HERSHEY_SIMPLEX

            (text_w, text_h), _ = cv.getTextSize(text, font, 1, 2)

            cv.putText(
                frame,
                text,
                ((width - text_w) // 2, (height + text_h) // 2),
                font,
                1,
                color,
                2
            )

    def three_fingers_up(self, hand_landmarks):
        tips, pips = [12, 16, 20], [10, 14, 18]

        three_up = all(
            hand_landmarks.landmark[t].y <
            hand_landmarks.landmark[p].y
            for t, p in zip(tips, pips)
        )

        index_down = hand_landmarks.landmark[8].y > hand_landmarks.landmark[6].y

        return three_up and index_down


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

        self.active_shape = None  # Stores "rect", "tri", or "circle"[cite: 1]

        self.move_start_x = None
        self.move_start_y = None

        self.running = True

        self.root = tk.Tk()
        self.root.title("AI Virtual Board")
        self.root.configure(bg="#1e1e1e")
        self.root.attributes("-fullscreen", True)

        self.is_fullscreen = True
        self.zoom = 1.0

        self.top_bar = tk.Frame(self.root, bg="#2d2d2d", height=40)
        self.top_bar.pack(fill="x", side="top")

        self.mode_label = tk.Label(
            self.top_bar,
            text="Mode: Idle",
            fg="white",
            bg="#2d2d2d",
            font=("Arial", 11, "bold")
        )
        self.mode_label.pack(side="left", padx=15)

        self.color_indicator = tk.Label(
            self.top_bar,
            text="      ",
            bg="red",
            width=4
        )
        self.color_indicator.pack(side="left", padx=8)

        self.brush_label = tk.Label(
            self.top_bar,
            text="Brush: --",
            fg="#aaaaaa",
            bg="#2d2d2d",
            font=("Arial", 10)
        )
        self.brush_label.pack(side="left", padx=8)

        self.zoom_label = tk.Label(
            self.top_bar,
            text="Zoom: 1.0x",
            fg="#aaaaaa",
            bg="#2d2d2d",
            font=("Arial", 10)
        )
        self.zoom_label.pack(side="left", padx=8)

        self.split_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.split_frame.pack(fill="both", expand=True)

        self.split_frame.columnconfigure(0, weight=1, uniform="half")
        self.split_frame.columnconfigure(2, weight=1, uniform="half")
        self.split_frame.rowconfigure(0, weight=1)

        self.camera_label = tk.Label(self.split_frame, bg="black")
        self.camera_label.grid(row=0, column=0, sticky="nsew")

        tk.Frame(self.split_frame, bg="#444444", width=2).grid(row=0, column=1, sticky="ns")

        self.canvas_label = tk.Label(self.split_frame, bg="black")
        self.canvas_label.grid(row=0, column=2, sticky="nsew")

        self.__init__bindings()

    def __init__bindings(self):
        self.root.bind("<f>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)
        self.root.bind("<plus>", lambda e: self.adjust_zoom(True))
        self.root.bind("<minus>", lambda e: self.adjust_zoom(False))
        self.root.bind("<x>", lambda e: self._quit())
        self.root.protocol("WM_DELETE_WINDOW", self._quit)

    def draw_shape_preview(self, frame, p1, p2, p3=None):

        if self.active_shape == "rect":
            cv.rectangle(frame, p1, p2, self.color, self.size)

        elif self.active_shape == "circle":
            dist = int(np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2))
            cv.circle(frame, p1, dist, self.color, self.size)

        elif self.active_shape == "tri" and p3:
            pts = np.array([p1, p2, p3], np.int32)
            cv.polylines(frame, [pts], True, self.color, self.size)

    def commit_shape(self, p1, p2, p3=None):

        if self.active_shape == "rect":
            cv.rectangle(self.canvas, p1, p2, self.color, self.size)

        elif self.active_shape == "circle":
            dist = int(np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2))
            cv.circle(self.canvas, p1, dist, self.color, self.size)

        elif self.active_shape == "tri" and p3:
            pts = np.array([p1, p2, p3], np.int32)
            cv.polylines(self.canvas, [pts], True, self.color, self.size)

        self.active_shape = None

    def _quit(self):
        self.running = False
        self.root.destroy()

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.root.attributes("-fullscreen", False)

    def adjust_zoom(self, increase=True):
        self.zoom = min(self.zoom + 0.1, 3.0) if increase else max(self.zoom - 0.1, 0.3)
        self.zoom_label.config(text=f"Zoom: {self.zoom:.1f}x")

    def update_window(self, combined_frame=None):
        canvas_w, canvas_h = self.canvas_label.winfo_width(), self.canvas_label.winfo_height()

        if canvas_w > 1 and canvas_h > 1:
            img = self.canvas.copy()
            h, w = img.shape[:2]

            new_w, new_h = int(w / self.zoom), int(h / self.zoom)
            cx, cy = w // 2, h // 2

            x1, y1 = max(0, cx - new_w // 2), max(0, cy - new_h // 2)
            img_cropped = img[y1:min(h, y1 + new_h), x1:min(w, x1 + new_w)]
            img_final = cv.resize(img_cropped, (canvas_w, canvas_h))

            img_tk = ImageTk.PhotoImage(
                image=Image.fromarray(cv.cvtColor(img_final, cv.COLOR_BGR2RGB))
            )

            self.canvas_label.imgtk = img_tk
            self.canvas_label.config(image=img_tk)

        if combined_frame is not None:
            cam_w, cam_h = self.camera_label.winfo_width(), self.camera_label.winfo_height()

            if cam_w > 1 and cam_h > 1:
                cam = cv.resize(combined_frame.copy(), (cam_w, cam_h))

                cam_tk = ImageTk.PhotoImage(
                    image=Image.fromarray(cv.cvtColor(cam, cv.COLOR_BGR2RGB))
                )

                self.camera_label.imgtk = cam_tk
                self.camera_label.config(image=cam_tk)

        mode = "Drawing" if self.drawing else "Erasing" if self.erasing else "Moving" if self.moving else "Idle"

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
            self.reset()

    def erase(self, x, y, c1, c2):
        if c2.y < c1.y:
            if not self.erasing or self.prev_x is None:
                self.prev_x, self.prev_y = x, y
                self.erasing = True

            cv.line(self.canvas, (self.prev_x, self.prev_y), (x, y), (0, 0, 0), 30)
            self.prev_x, self.prev_y = x, y

        else:
            self.reset()

    def reset(self):
        self.prev_x, self.prev_y = None, None
        self.drawing = False
        self.erasing = False

    def clear_all(self, width, height):
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)

    def start_moving(self, x, y):
        if not self.moving:
            self.move_start_x, self.move_start_y = x, y
            self.moving = True

    def apply_moving(self, x, y):
        if self.moving:
            dx, dy = x - self.move_start_x, y - self.move_start_y

            N = np.float32([[1, 0, dx], [0, 1, dy]])

            self.canvas = cv.warpAffine(
                self.canvas,
                N,
                (self.canvas.shape[1], self.canvas.shape[0])
            )

            self.move_start_x, self.move_start_y = x, y

    def stop_moving(self):
        self.moving = False


class gui:
    def __init__(self, w, h):
        self.slider_x, self.slider_y = 50, 50
        self.slider_w, self.slider_h = 150, 20

        self.button_x1, self.button_x2 = 400, 600
        self.button_y1, self.button_y2 = 60, 110

        self.mode_btn_x, self.mode_btn_y = 220, 60
        self.mode_btn_w, self.mode_btn_h = 150, 50

        self.color_btn_y = 20
        self.color_btn_x_start = 30

        self.red, self.green, self.blue = (0, 0, 255), (0, 255, 0), (255, 0, 0)

        self.w, self.h = w, h
        self.mode = "drawing"
        self.last_mode_switch = 0

    def click(self, px, py, x, y, w, h):
        return x < px < x + w and y < py < y + h

    def handle(self, frame, x, y, painter):

        cv.rectangle(
            frame,
            (self.mode_btn_x, self.mode_btn_y),
            (self.mode_btn_x + self.mode_btn_w, self.mode_btn_y + self.mode_btn_h),
            (255, 255, 255),
            2
        )

        mode_text = "SHAPES MODE" if self.mode == "drawing" else "DRAW MODE"

        cv.putText(
            frame,
            mode_text,
            (self.mode_btn_x + 10, self.mode_btn_y + 35),
            cv.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        if self.click(x, y, self.mode_btn_x, self.mode_btn_y, self.mode_btn_w, self.mode_btn_h):
            if time.time() - self.last_mode_switch > 0.5:
                self.mode = "shapes" if self.mode == "drawing" else "drawing"
                self.last_mode_switch = time.time()

        # Red
        cv.rectangle(
            frame,
            (self.color_btn_x_start, self.color_btn_y),
            (self.color_btn_x_start + 50, self.color_btn_y + 50),
            self.red,
            -1
        )

        # Green
        cv.rectangle(
            frame,
            (self.color_btn_x_start + 70, self.color_btn_y),
            (self.color_btn_x_start + 120, self.color_btn_y + 50),
            self.green,
            -1
        )

        # Blue
        cv.rectangle(
            frame,
            (self.color_btn_x_start + 140, self.color_btn_y),
            (self.color_btn_x_start + 190, self.color_btn_y + 50),
            self.blue,
            -1
        )

        if self.click(x, y, self.color_btn_x_start, self.color_btn_y, 50, 50):
            painter.color = self.red

        elif self.click(x, y, self.color_btn_x_start + 70, self.color_btn_y, 50, 50):
            painter.color = self.green

        elif self.click(x, y, self.color_btn_x_start + 140, self.color_btn_y, 50, 50):
            painter.color = self.blue

        cv.rectangle(
            frame,
            (self.slider_x, 100),
            (self.slider_x + self.slider_w, 120),
            (200, 200, 200),
            -1
        )

        handle_x = self.slider_x + int((painter.size / 20) * self.slider_w)

        cv.circle(frame, (handle_x, 110), 10, (0, 0, 0), -1)

        if self.click(x, y, self.slider_x, 100, self.slider_w, 20):
            rel_x = max(0, min(x - self.slider_x, self.slider_w))
            painter.size = max(1, int((rel_x / self.slider_w) * 20))

        if self.mode != "drawing":
            shape_btns = [
                ("Rectangle", 150, "rect"),
                ("Triangle", 250, "tri"),
                ("Circle", 350, "circle")
            ]

            for label, y_pos, s_type in shape_btns:
                bx, by, bw, bh = self.w - 160, y_pos, 140, 60

                cv.rectangle(
                    frame,
                    (bx, by),
                    (bx + bw, by + bh),
                    (255, 165, 0),
                    2
                )

                cv.putText(
                    frame,
                    label,
                    (bx + 10, by + 40),
                    cv.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 165, 0),
                    2
                )

                if self.click(x, y, bx, by, bw, bh):
                    painter.active_shape = s_type

        cv.rectangle(
            frame,
            (self.button_x1, self.button_y1),
            (self.button_x2, self.button_y2),
            (0, 0, 255),
            2
        )

        cv.putText(frame, "CLEAR", (450, 90), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        if self.click(x, y, self.button_x1, self.button_y1,
                      self.button_x2 - self.button_x1,
                      self.button_y2 - self.button_y1):
            return "clear"

        return None