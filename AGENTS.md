# AGENTS.md — Face Recognition (OpenCV + LBPH)

You are setting up, running, and maintaining a small face-recognition project
on a **Windows** laptop. The user may be completely new to computers. Work
through the phases below **in order**, one at a time, and do not skip ahead.

## What this project is

A webcam program that recognises faces. Three scripts, run in order:

| Script | Stage | Produces |
|---|---|---|
| `capture_faces.py` | 1. Take photos | `dataset/<person>/*.jpg` |
| `train_model.py` | 2. Train the model | `trainer.yml`, `trainer.json` |
| `recognize_faces.py` | 3. Recognise live | `attendance/<date>.csv` |

`config.py` holds shared settings. `requirements.txt` holds dependencies.

## Hard rules — do not break these

1. **Never install `opencv-python`.** Only `opencv-contrib-python`. The face
   recogniser (`cv2.face`) exists only in the contrib build. Installing the
   wrong one makes training crash.
2. **Never install version 5 or newer.** Version 5 ships without the cascade
   XML files the program needs, so detection fails with "No face cascade
   found". `requirements.txt` already pins `>=4.5,<5` — keep that pin.
3. **Never delete `dataset/`, `trainer.yml`, or `trainer.json` without asking
   the user first.** Those contain their photographs and hours of work.
4. **Never claim a step succeeded without running the command and reading its
   real output.** If you did not run it, say so.
5. **Do not "fix" the source code** unless the user asks. This project is
   working; your job is to install, run, and verify it.
6. **If a command fails, read the actual error text** before trying anything.
   Do not guess at fixes.

## Phase 0 — Preflight (run all of these, then report)

Run and capture the real output of each:

```powershell
python --version
python -c "import cv2; print(cv2.__version__)"
python -c "import cv2; print(hasattr(cv2,'face'))"
Get-ChildItem -Name
```

Report to the user, in plain language:
- Is Python installed? (needs 3.9 or newer)
- Is `cv2` installed, and is it version 4.x?
- Does `cv2.face` exist? (must print `True`)
- Are all six project files present?

**If Python is missing entirely**, stop and give these instructions. Do not try
to install it yourself — it needs a human clicking through a GUI installer:
1. Go to https://www.python.org/downloads/ and download the Windows installer.
2. **Tick "Add python.exe to PATH" on the first screen.** If this is missed,
   everything fails and must be redone.
3. Install, then re-run Phase 0.

**If `cv2` reports version 5 or newer**, fix it with:
`python -m pip install --force-reinstall "opencv-contrib-python>=4.5,<5"`

## Phase 1 — Install dependencies

```powershell
python -m pip install -r requirements.txt
```

This takes a few minutes and prints a lot of text. That is normal. Wait for it
to finish. Do not interrupt it.

Then re-run the Phase 0 cv2 checks and confirm the version starts with `4`.

## Phase 2 — Get training photos

**You must ask the user which method they want before doing anything here.**

### Option A — Drive the webcam automatically (user must be present)

Ask for each person's name, one at a time. For each name:

1. Confirm the Windows Camera app and any video call are closed.
2. Open the camera with `cv2.VideoCapture(0)` from the project folder.
3. Loop: read a frame, mirror it with `cv2.flip(frame, 1)`, convert to
   grayscale, `cv2.equalizeHist`, then detect a face with the cascade from
   `get_face_detector()` in `capture_faces.py` (import it — do not re-implement
   the cascade list).
4. When a face is found, crop the **largest** face, apply a small random
   translation and a small random brightness/contrast change, and save it as
   `dataset/<name>/img_NNN.jpg`. The jitter imitates head movement between
   shots and measurably improves accuracy.
5. Keep the last ~5 clean, unjittered crops aside as held-out test frames.
6. Stop after 60 saved photos. Tell the user to stay still and face the camera,
   and to move slightly between shots is NOT needed since you jitter yourself.

Say clearly what you are about to do before opening the camera, because the
user must be sitting in front of it.

### Option B — Use photos the user already has

Ask for the folder path. For each person, create `dataset/<name>/` and copy
their `.jpg` files in. If photos are `.png` or `.heic`, convert to `.jpg` first.
20+ clear, front-facing, well-lit photos per person is a reasonable minimum.

### Notes for both options
- Folder name becomes the on-screen label, so no spaces and consistent spelling.
- Remove obvious junk: photos with no face, heavy blur, or the face tiny in
  frame. `train_model.py` uses the whole image when it cannot find a face, so
  a photo of a wall actively harms the model.

## Phase 3 — Train

```powershell
python train_model.py
```

Read the output. It prints one line per person with a photo count. **Note these
counts** — you need them for Phase 4.

## Phase 4 — Verify (do not skip; report honestly)

Check every one of these and report PASS or FAIL for each:

1. `trainer.yml` exists and is not empty.
2. `trainer.json` exists and maps each person name to a number.
3. **Every person has a photo count greater than 0.** A `0` means that
   person's folder is empty, misplaced, or has the wrong file extension.
4. The `Classes:` line lists every person you intended to register.
5. Load the model and predict, without a webcam:
   ```python
   import cv2, json
   rec = cv2.face.LBPHFaceRecognizer_create()
   rec.read("trainer.yml")
   names = {int(k): v for k, v in json.load(open("trainer.json")).items()}
   img = cv2.imread(r"<one saved photo path>", cv2.IMREAD_GRAYSCALE)
   img = cv2.equalizeHist(cv2.resize(img, (300, 300)))
   print(rec.predict(img))
   ```
   The returned label must map back to the correct name, and the distance must
   be below `CONFIDENCE_LIMIT` (70) in `config.py`.
6. If you kept held-out test frames in Option A, predict each one and report
   the hit rate.

## Phase 5 — Run it live

```powershell
python recognize_faces.py
```

**This step needs the human and you cannot do it for them.** Tell the user:

- Click the camera window, then press **A** to mark attendance, **Q** to quit.
- A **green** box with a name means recognised. A **red UNKNOWN** box means the
  person is not in the training data.
- Afterwards check `attendance/<date>.csv` contains the rows.

## Phase 6 — Report

Finish with a short summary: what was installed, photos per person, the
held-out hit rate, whether every Phase 4 check passed, and anything the user
must do themselves. State plainly anything you did not verify.

## Troubleshooting — match the exact error text

| Error | Fix |
|---|---|
| `'python' is not recognized` | Python not installed, or PATH box was not ticked. Reinstall with the PATH box ticked. |
| `'pip' is not recognized` | Use `python -m pip`, not bare `pip`. |
| `No module named 'cv2'` | Install did not complete. Re-run Phase 1. |
| `module 'cv2' has no attribute 'face'` | Wrong package installed. `python -m pip uninstall opencv-python opencv-contrib-python`, then re-run Phase 1. |
| `No face cascade found` | OpenCV 5 is installed. Reinstall with `"opencv-contrib-python>=4.5,<5"`. |
| `Could not open the webcam` | Close the Windows Camera app. Check Settings → Privacy → Camera. If two cameras exist, set `CAMERA_INDEX = 1` in `config.py`. |
| `No dataset folder` | Phase 2 was skipped. |
| `No face photos found in the dataset folder` | Photos are not directly inside `dataset/<person>/` or are not `.jpg`. |
| No box around a face | Face too far away (must be over ~100 px), too dark, or not facing the camera. |
| Always shows red UNKNOWN | Training was not re-run after photos were added, or photos are poor. Retrain. |
| Everything is UNKNOWN for a registered person | Their folder is not inside `dataset/`, or the folder name differs from what they type at the prompt. |

## File map

```
face-recognition/
  capture_faces.py     stage 1
  train_model.py       stage 2
  recognize_faces.py   stage 3
  config.py            shared settings
  requirements.txt     dependencies (pinned <5)
  AGENTS.md            this file
  README.md            short reference
  dataset/<person>/*.jpg      created in phase 2
  trainer.yml                  created in phase 3
  trainer.json                 created in phase 3
  attendance/<date>.csv        created in phase 5
```
