import cv2 as cv
import numpy as np
from classes import Tracker, control, gui, painting
 
tracker = Tracker()
ret, frame = tracker.video_capture.read()
if not ret:
    print("Failed to access camera")
    exit()
h, w, _ = frame.shape
 
tracking = control(w, h)
painter = painting(w, h)
ui = gui(w, h)
 
painter.update_window()
 
while painter.running:
    frame, results = tracker.get_frame()
    if frame is None:
        break
 
    if results.multi_hand_landmarks:
        left_hand = None
        right_hand = None
 
        for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            left_or_right = results.multi_handedness[hand_idx].classification[0].label
            tracker.draw_landmarks(frame, hand_landmarks)
 
            if left_or_right == "Left":
                left_hand = hand_landmarks
            elif left_or_right == "Right":
                right_hand = hand_landmarks
 
        if left_hand:
            tracking.multi_hand(left_hand, right_hand, tracking, painter, ui, w, h, frame)
            tracking.submit(painter.canvas, frame, left_hand)
 
    else:
        painter.stop_moving()
        painter.reset()
        painter.drawing = False
        painter.erasing = False

    combined = cv.addWeighted(frame, 0.7, painter.canvas, 1, 0)
 
    try:
        painter.update_window(combined_frame=combined)
        painter.root.update_idletasks()
        painter.root.update()
    except:
        break

    key = cv.waitKey(1)
    if key == ord('q') or key == ord('x'):
        break
 
tracker.video_capture.release()
cv.destroyAllWindows()

try:
    painter.root.destroy()
except:
    pass
