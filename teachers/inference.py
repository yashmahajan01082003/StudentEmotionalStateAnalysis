import cv2 
import numpy as np 
import mediapipe as mp 
from keras.models import load_model 
import time

# Load model and labels
model = load_model("model.h5")
label = np.load("labels.npy")

# Mediapipe setup
holistic = mp.solutions.holistic
hands = mp.solutions.hands
holis = holistic.Holistic()
drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# Timing variables
emotion_times = {}  # Dictionary to store total seconds per emotion
current_state = None  # Can be emotion label or 'Absent'
start_time = None

while True:
    lst = []
    _, frm = cap.read()
    frm = cv2.flip(frm, 1)
    res = holis.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))

    if res.face_landmarks:
        # Person is present
        pred = None

        # Extract face landmarks relative to landmark 1
        for i in res.face_landmarks.landmark:
            lst.append(i.x - res.face_landmarks.landmark[1].x)
            lst.append(i.y - res.face_landmarks.landmark[1].y)

        # Left hand
        if res.left_hand_landmarks:
            for i in res.left_hand_landmarks.landmark:
                lst.append(i.x - res.left_hand_landmarks.landmark[8].x)
                lst.append(i.y - res.left_hand_landmarks.landmark[8].y)
        else:
            for i in range(42):
                lst.append(0.0)

        # Right hand
        if res.right_hand_landmarks:
            for i in res.right_hand_landmarks.landmark:
                lst.append(i.x - res.right_hand_landmarks.landmark[8].x)
                lst.append(i.y - res.right_hand_landmarks.landmark[8].y)
        else:
            for i in range(42):
                lst.append(0.0)

        lst = np.array(lst).reshape(1, -1)

        # Predict emotion
        pred = label[np.argmax(model.predict(lst))]
        cv2.putText(frm, pred, (50,50), cv2.FONT_ITALIC, 1, (255,0,0), 2)
        state = pred  # Current state is the detected emotion

    else:
        # Person absent
        cv2.putText(frm, "Absent", (50,50), cv2.FONT_ITALIC, 1, (0,0,255), 2)
        state = "Absent"

    # Timing logic
    current_time = time.time()
    if current_state is None:
        current_state = state
        start_time = current_time
    elif current_state != state:
        duration = current_time - start_time
        if current_state in emotion_times:
            emotion_times[current_state] += duration
        else:
            emotion_times[current_state] = duration

        current_state = state
        start_time = current_time

    # Draw landmarks
    if res.face_landmarks:
        drawing.draw_landmarks(frm, res.face_landmarks, holistic.FACEMESH_CONTOURS)
    if res.left_hand_landmarks:
        drawing.draw_landmarks(frm, res.left_hand_landmarks, hands.HAND_CONNECTIONS)
    if res.right_hand_landmarks:
        drawing.draw_landmarks(frm, res.right_hand_landmarks, hands.HAND_CONNECTIONS)

    cv2.imshow("window", frm)

    if cv2.waitKey(1) == ord('q'):
        # Save duration for the last state
        if current_state is not None and start_time is not None:
            duration = time.time() - start_time
            if current_state in emotion_times:
                emotion_times[current_state] += duration
            else:
                emotion_times[current_state] = duration
        break

cap.release()
cv2.destroyAllWindows()

# Print durations
print("\n--- State Durations (seconds) ---")
for state, t in emotion_times.items():
    print(f"{state}: {t:.2f} s")
