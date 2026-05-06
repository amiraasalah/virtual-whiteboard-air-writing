import cv2 as cv
import numpy as np
from classes import Tracker, control, gui, painting


# 1. INIT TRACKER + GET SIZE
# =========================
tracker = Tracker()

ret, frame = tracker.video_capture.read()
if not ret:
    print("Error: Could not access camera.")
    exit()

h, w, _ = frame.shape



# 2. INIT CORE MODULES
tracking = control(w, h)
painter = painting(w, h)
ui = gui(w, h)

painter.update_window()


while painter.running:

    frame, results = tracker.get_frame()
    if frame is None:
        break

    left_hand, right_hand = None, None


    # HAND DETECTION
    if results.multi_hand_landmarks and results.multi_handedness:

        for idx, landmarks in enumerate(results.multi_hand_landmarks):

            label = results.multi_handedness[idx].classification[0].label

            tracker.draw_landmarks(frame, landmarks)

            if label == "Left":
                left_hand = landmarks
            elif label == "Right":
                right_hand = landmarks

        if left_hand:

            tracking.multi_hand(
                left_hand,
                right_hand,
                tracking,
                painter,
                ui,
                w,
                h,
                frame
            )

            tracking.submit(painter.canvas, frame, left_hand)

    else:
        painter.stop_moving()
        painter.reset()
        painter.drawing = False
        painter.erasing = False

    # RENDER
    # =========================
    combined = cv.addWeighted(frame, 0.7, painter.canvas, 1, 0)

    try:
        painter.update_window(combined_frame=combined)
        painter.root.update_idletasks()
        painter.root.update()
    except:
        break


    # =========================
    # EXIT
    if cv.waitKey(1) & 0xFF == ord('q'):
        break


# CLEANUP
# =========================
tracker.video_capture.release()
cv.destroyAllWindows()

try:
    painter.root.destroy()
except:
    pass
