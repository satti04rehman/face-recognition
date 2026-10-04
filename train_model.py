"""Step 2 - train the recognizer on the captured photos.

Run (after capture_faces.py):  python train_model.py

Reads every photo in dataset/<name>/, teaches the LBPH model what each
person's face looks like, and saves the result to trainer.yml.
"""

import json

import cv2
import numpy as np

import config
from capture_faces import get_face_detector


def crop_face(gray, detector):
    """Return the face region of one training image.

    Photos from capture_faces.py are already tight face crops, but people
    often have ordinary photos lying around and just drop those in. Detecting
    the face here means both kinds train on the face instead of the whole
    picture. If no face is found we keep the image as-is.
    """
    faces = detector.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
    )
    if len(faces) == 0:
        return gray
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    return gray[y : y + h, x : x + w]


def load_training_data():
    """Return (images, labels, label_names) from the dataset folder."""
    images = []        # every face image, resized to one fixed size
    labels = []        # a number for each image (0, 1, 2, ...)
    label_names = {}   # number -> person name

    if not config.DATASET_DIR.exists():
        raise FileNotFoundError(
            f"No dataset folder. Run capture_faces.py first ({config.DATASET_DIR})"
        )

    detector = get_face_detector()

    for next_id, person_dir in enumerate(sorted(config.DATASET_DIR.iterdir())):
        if not person_dir.is_dir():
            continue
        label_names[next_id] = person_dir.name
        loaded = 0
        for img_file in sorted(person_dir.glob("*.jpg")):
            gray = cv2.imread(str(img_file), cv2.IMREAD_GRAYSCALE)
            if gray is None:
                continue
            # Cut out the face, so whole photos and cropped photos both work.
            gray = crop_face(gray, detector)
            # Same fixed size as the recognition step uses.
            gray = cv2.resize(gray, (config.FACE_SIZE, config.FACE_SIZE))
            gray = cv2.equalizeHist(gray)
            images.append(gray)
            labels.append(next_id)
            loaded += 1
        print(f"  {person_dir.name}: {loaded} photos")

    if not images:
        raise RuntimeError("No face photos found in the dataset folder.")

    return images, labels, label_names


def main():
    print(f"Loading photos from {config.DATASET_DIR}")
    images, labels, label_names = load_training_data()
    print(f"Loaded {len(images)} photos of {len(label_names)} person(s).")

    # LBPH = Local Binary Patterns Histograms.
    # It describes a face as a pattern of tiny local textures and compares
    # faces by how similar those patterns are.
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    # OpenCV wants numpy arrays here, not plain Python lists.
    recognizer.train(np.array(images), np.array(labels, np.int32))

    config.TRAINER_FILE.parent.mkdir(exist_ok=True)
    recognizer.save(str(config.TRAINER_FILE))

    # LBPH only stores integer labels, so keep the number -> name map
    # in a small JSON file next to the model.
    labels_file = config.TRAINER_FILE.with_suffix(".json")
    with open(labels_file, "w") as f:
        json.dump(label_names, f, indent=2)

    print(f"Model saved to {config.TRAINER_FILE}")
    print(f"Labels saved to {labels_file}")
    print(f"Classes: {label_names}")


if __name__ == "__main__":
    main()