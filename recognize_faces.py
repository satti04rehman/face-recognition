"""Step 3 - live face recognition from the webcam.

Run (after train_model.py):  python recognize_faces.py

The webcam window shows the person's name and a confidence % in real time.

Keys:
    A  mark the recognized person as present (once per person per session)
    Q  quit

Attendance rows are appended to attendance/<date>.csv
"""

import csv
import json
from datetime import datetime

import cv2

import config
from capture_faces import get_face_detector


def confidence_percent(confidence):
    """Convert LBPH distance into a friendlier 0-100% match number."""
    # confidence 0      -> 100%
    # confidence >= 100 -> 0%
    return max(0, min(100, int(100 - confidence)))


def mark_attendance(name):
    """Append one attendance row for today. Has no effect if the person
    was already marked today (checked later in recognize_faces.py)."""
    config.ATTENDANCE_DIR.mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    csv_file = config.ATTENDANCE_DIR / f"{today}.csv"

    # Append (new file? write the header first).
    new_file = not csv_file.exists()
    with open(csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["name", "time"])
        writer.writerow([name, datetime.now().strftime("%H:%M:%S")])
    print(f"Attendance marked for {name} -> {csv_file.name}")


def main():
    if not config.TRAINER_FILE.exists():
        print(f"No trained model ({config.TRAINER_FILE}). Run train_model.py first.")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(str(config.TRAINER_FILE))

    # Load the number -> name map saved by train_model.py.
    labels_file = config.TRAINER_FILE.with_suffix(".json")
    with open(labels_file) as f:
        label_names = {int(k): v for k, v in json.load(f).items()}

    detector = get_face_detector()
    camera = cv2.VideoCapture(config.CAMERA_INDEX)
    if not camera.isOpened():
        print("Could not open the webcam. Check CAMERA_INDEX in config.py.")
        return

    present_today = set()  # names already marked today (avoid duplicates)

    print("Recognizing... press A to mark attendance, Q to quit.\n")

    while True:
        ok, frame = camera.read()
        if not ok:
            print("Webcam stopped returning frames.")
            break

        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        faces = detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=config.MIN_FACE_SIZE,
        )

        # A second copy of the box color: green for known, red for unknown.
        name = None  # recognized name in THIS frame (reset every frame)
        for (x, y, w, h) in faces:
            face_img = gray[y : y + h, x : x + w]
            face_img = cv2.resize(face_img, (config.FACE_SIZE, config.FACE_SIZE))
            face_img = cv2.equalizeHist(face_img)

            label, confidence = recognizer.predict(face_img)
            name = label_names.get(label)

            if name is not None and confidence <= config.CONFIDENCE_LIMIT:
                text = f"{name} {confidence_percent(confidence)}%"
                color = (0, 255, 0)  # green
            else:
                text = "UNKNOWN"
                name = None
                color = (0, 0, 255)  # red

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, color, 2)

        cv2.imshow("Recognition - A=attendance  Q=quit", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("a") and name is not None:
            if name in present_today:
                print(f"{name} already marked today.")
            else:
                mark_attendance(name)
                present_today.add(name)

    camera.release()
    cv2.destroyAllWindows()
    print("Stopped.")


if __name__ == "__main__":
    main()