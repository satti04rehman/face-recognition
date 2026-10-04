"""Step 1 - capture face photos from the webcam.

Run:  python capture_faces.py

You will be asked for a person's name. Then look at the camera and press:

    S  save the current face photo
    Q  quit (after at least 40 photos, or the training step will be weak)

Photos are saved as small face crops in dataset/<name>/ so the trainer
does not care about the rest of the image.
"""

import cv2

import config

# Build a face detector from the cascade XML file that ships with OpenCV.
def get_face_detector():
    from pathlib import Path
    for name in config.FACE_CASCADE_TRIES:
        path = Path(cv2.data.haarcascades) / name
        if path.exists():
            return cv2.CascadeClassifier(str(path))
    raise FileNotFoundError(
        "No face cascade found. Reinstall opencv-contrib-python."
    )


def main():
    name = input("Person's name (no spaces, e.g. ali): ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    person_dir = config.DATASET_DIR / name
    person_dir.mkdir(parents=True, exist_ok=True)

    detector = get_face_detector()
    camera = cv2.VideoCapture(config.CAMERA_INDEX)
    if not camera.isOpened():
        print("Could not open the webcam. Check CAMERA_INDEX in config.py.")
        return

    count = 0
    print(f"\nCapturing photos for '{name}'. Press S to save, Q to quit.")
    print(f"Try to capture at least {config.SAMPLES_PER_PERSON}.\n")

    while True:
        ok, frame = camera.read()
        if not ok:
            print("Webcam stopped returning frames.")
            break

        # Mirror the image so it feels natural, like a mirror.
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Equalizing helps the detector in bad lighting.
        gray = cv2.equalizeHist(gray)

        faces = detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=config.MIN_FACE_SIZE,
        )

        # Draw a box around every face found.
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.putText(
            frame,
            f"Photos saved: {count}  (S=save  Q=quit)",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )
        cv2.imshow("Capture - press S to save, Q to quit", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("s") and len(faces) > 0:
            # Save the largest face only, as a square crop.
            (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
            face_img = gray[y : y + h, x : x + w]
            file_name = person_dir / f"img_{count:03d}.jpg"
            cv2.imwrite(str(file_name), face_img)
            count += 1
            print(f"  saved {file_name.name}")

    camera.release()
    cv2.destroyAllWindows()

    print(f"\nDone. {count} photos saved to {person_dir}")
    if count < 40:
        print("WARNING: fewer than 40 photos - training will be weak.")
        print("Run this script again and capture more.")


if __name__ == "__main__":
    main()