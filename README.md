# Face Recognition (OpenCV + LBPH)

A simple live face recognition project: register people with a webcam,
train the model, then recognize faces in real time. Suited for a 3rd-semester
project submission: three scripts, one algorithm, no heavy frameworks.

## How it works (viva-ready, 30 seconds)

1. **Detection** — OpenCV's pre-trained frontal-face cascade scans every
   camera frame and draws a box around face-like regions. `config.py` tries
   the LBP cascade first and falls back to the Haar cascade, because some
   OpenCV builds ship only one of the two.
2. **Training** — each registered face is resized to a fixed square and the
   LBPH (Local Binary Patterns Histograms) technique describes it as a grid
   of local texture patterns. The model stores one of these "face signatures"
   per person.
3. **Recognition** — a new face is converted to the same signature and compared
   with every stored one. The closest match wins; a high "distance" means the
   face is unknown. LBPH confidence is a distance, so **lower is better**.

## Requirements

- Python 3.9+ (3.10+ recommended)
- A webcam

Install dependencies (Windows):

```bat
pip install -r requirements.txt
```

> Use **opencv-contrib-python**, not opencv-python. The LBPH recognizer
> (`cv2.face`) is only shipped in the contrib package.

## Step 1 — Collect photos

```bat
python capture_faces.py
```

Enter a name (e.g. `ali`). Look at the camera and press **S** to save a photo
(move your head slightly between shots), **Q** to quit after ~60 photos.
Run it once per person. Photos are stored as cropped faces in `dataset/<name>/`.

Good lighting and ~60 photos make recognition noticeably better.

### Using photos you already have

You do not have to use the webcam. Put photos in
`dataset/<name>/` and run `python train_model.py` — the trainer finds the face
in each photo and crops it, so ordinary pictures work as well as webcam
captures.

```
dataset/
  ali/     photo1.jpg  photo2.jpg  ...
  bilal/   photo1.jpg  ...
```

Rules: one folder per person, name the folder after the person, use `.jpg`,
and prefer clear, front-facing, well-lit shots (about 20+ per person). If a
photo has no detectable face it is still used, so junk photos teach the model
junk — delete anything unusable. **Any number of people works**; each folder
becomes one class automatically. Beyond roughly 10–15 people, add more photos
per person rather than more people.

Re-run `train_model.py` after every change to `dataset/`.

## Step 2 — Train the model

```bat
python train_model.py
```

This reads `dataset/`, trains the LBPH model, and writes `trainer.yml`
plus `trainer.json` (the number → name lookup table).

## Step 3 — Live recognition

```bat
python recognize_faces.py
```

Known faces get a green box with name + match %, unknown faces a red
"UNKNOWN" box. Press **A** to mark the recognized person present (once per
person per day), **Q** to quit. Attendance rows are appended to
`attendance/YYYY-MM-DD.csv`.

## Project layout

```
capture_faces.py     step 1: webcam -> dataset/<name>/...
train_model.py       step 2: dataset/ -> trainer.yml + trainer.json
recognize_faces.py   step 3: trainer.yml + webcam -> real-time result + attendance/
config.py            shared paths and settings (edit here)
requirements.txt     opencv-contrib-python (4.x, NOT 5.x), numpy
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `module 'cv2' has no attribute 'face'` | You installed `opencv-python`. Install `opencv-contrib-python` instead. |
| `No face cascade found` | You installed OpenCV **5.x**, whose wheels ship no cascade XML files. Reinstall with `pip install "opencv-contrib-python>=4.5,<5"`. |
| Webcam not opening | Set `CAMERA_INDEX = 1` in `config.py` (external camera). |
| Poor recognition | Capture more photos, better light, keep glasses/hair consistent. |
| "No dataset folder" | Run capture_faces.py first. |
| Nothing detects | Move closer (face must be > 100px wide) and brighten the room. |

## Extending it (viva bonus points)

- Add the person's roll number to the CSV (it is just a list of text columns).
- Save the video clip when an unknown face appears (`cv2.VideoWriter`).
- Increase `CONFIDENCE_LIMIT` in `config.py` to admit more uncertain matches.