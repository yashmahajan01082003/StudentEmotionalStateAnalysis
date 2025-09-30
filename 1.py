import cv2
import mediapipe as mp
import csv
import os

# Initialize Mediapipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)
mp_draw = mp.solutions.drawing_utils

# CSV file to store landmarks + label
csv_file = "emotion_dataset.csv"
fieldnames = [f"x{i}" for i in range(468)] + [f"y{i}" for i in range(468)] + ["emotion"]

# Create file if not exists
if not os.path.exists(csv_file):
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

# Start webcam
cap = cv2.VideoCapture(0)

print("Press 'q' to quit, or 's' to save the current face landmarks with emotion label")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Draw landmarks on face
            mp_draw.draw_landmarks(frame, face_landmarks, mp_face_mesh.FACEMESH_TESSELATION)

    cv2.imshow("Mediapipe Emotion Dataset Capture", frame)
    key = cv2.waitKey(1)

    if key & 0xFF == ord('q'):
        break
    elif key & 0xFF == ord('s') and results.multi_face_landmarks:
        # Ask user for emotion label
        emotion = input("Enter emotion label for this face: ")

        face_landmarks = results.multi_face_landmarks[0]
        data = {}
        for i, lm in enumerate(face_landmarks.landmark):
            data[f"x{i}"] = lm.x
            data[f"y{i}"] = lm.y
        data["emotion"] = emotion

        with open(csv_file, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow(data)
        print(f"Saved landmarks with label '{emotion}'")

cap.release()
cv2.destroyAllWindows()
