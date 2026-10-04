"""Shared paths and settings for all three scripts.

Every script imports this file, so you change a setting here and it
applies everywhere. Nothing here touches the camera; it is only config.
"""

from pathlib import Path

# Root folder of the project (the folder this file lives in).
BASE_DIR = Path(__file__).resolve().parent

# Where the captured face photos are stored.
# Structure: dataset/<person_name>/img_000.jpg, img_001.jpg, ...
DATASET_DIR = BASE_DIR / "dataset"

# The trained model file. create it with train_model.py, use it in recognize_faces.py.
TRAINER_FILE = BASE_DIR / "trainer.yml"

# Attendance CSV files land here, named by date: 2026-09-28.csv
ATTENDANCE_DIR = BASE_DIR / "attendance"

# ---- Algorithm / capture settings ----

# Cascade file used to detect faces (comes bundled with OpenCV).
# LBP cascade is faster than Haar, so we try it first.
FACE_CASCADE_TRIES = [
    "lbpcascade_frontalface.xml",
    "haarcascade_frontalface_default.xml",
]

# How many photos to capture per person. More photos = better recognition.
SAMPLES_PER_PERSON = 60

# Faces smaller than this (pixels) are ignored. A tiny face means someone
# is too far from the camera.
MIN_FACE_SIZE = (100, 100)

# Images are resized to this fixed square before training/prediction,
# so every sample has the same shape regardless of camera resolution.
FACE_SIZE = 300

# LBPH confidence: LOWER is better (it is a distance from the stored face).
# Confidence above this value means "not sure -> show UNKNOWN".
CONFIDENCE_LIMIT = 70.0

# Which webcam to use. 0 = the built-in camera, 1 = an external one.
CAMERA_INDEX = 0