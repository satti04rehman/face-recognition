# team-context.md — face-recognition (friend's 3rd-sem project)

> **This file is the resume point.** Any new session working on this project MUST
> read this first, check the "CURRENT STATE" section, and continue from there.
> Last updated: **2026-09-29 ~14:40 PKT** — project is WORKING and verified.

---

## 1. What this project is

A live face-recognition demo project for Abdul's friend (3rd semester, needs it
for a college submission / viva). Requested 2026-09-28: *"python projects for my
friend 3rd sem like face recognition can you build it"*.

**Location:** `~/Projects/face-recognition/`
**Status:** **WORKING.** OpenCV installed, headless test green, and the live
webcam GUI loop verified end-to-end (see §5). No known open defects.

## 2. Layout

| File | Role |
|---|---|
| `capture_faces.py` | webcam → LBP cascade face detection → saves crops to `dataset/<name>/` (press S save, Q quit; ~60 photos) |
| `train_model.py` | reads `dataset/`, trains LBPH recognizer → `trainer.yml` + `labels.json` (int label → name map) |
| `recognize_faces.py` | live recognition: green box + name + match %, red box UNKNOWN; A = attendance → `attendance/YYYY-MM-DD.csv` (once per person/day); Q quit |
| `config.py` | all shared settings: paths, `SAMPLES_PER_PERSON=60`, `MIN_FACE_SIZE=(100,100)`, `FACE_SIZE=300`, `CONFIDENCE_LIMIT=70.0` (LBPH conf: **lower is better**), `CAMERA_INDEX=0` |
| `requirements.txt` | `opencv-contrib-python`, `numpy` |
| `README.md` | friend-facing: Windows setup, 3-step usage, viva-ready algorithm explanation, troubleshooting table |

## 3. Decisions (why it is shaped this way)

1. **OpenCV + LBPH**, not dlib/face_recognition/tensorflow:
   - Textbook algorithm for a 3rd-sem viva (Local Binary Patterns Histograms).
   - Single `pip install` on Windows, no compiler needed. Heavy libs would sink his friend's laptop.
2. **`opencv-contrib-python` (NOT `opencv-python`)** — `cv2.face.LBPHFaceRecognizer`
   lives only in the contrib package. Classic student trap; README warns about it.
3. **CLI, no GUI/web framework** — 3 scripts + keys (S/Q/A). Least to break, easiest to demo and defend. GUI (tkinter/Flask) is a possible future ask.
4. **LBPH stores only integer labels** — the name map is saved separately as
   `labels.json` beside `trainer.yml`. (We burned time on a nonexistent
   `getLabelInfo()`; record here so nobody re-litigates.)
5. **Capture saves face crops; training uses whole images** — consistent pipeline:
   crop in step 1, so step 2/3 just resize to `FACE_SIZE` square + equalize.

## 4. Bugs found & fixed (2026-09-28)

- `recognize_faces.py`: `name` was only assigned inside the face loop → pressing A
  with no face on screen could `NameError` or mark a **stale name from a previous
  frame**. Fixed: `name = None` reset every frame.
- One careless edit removed the rectangle/putText drawing lines during that fix —
  restored and re-verified (`py_compile` clean).

## 5. Verification status (2026-09-29 — everything below was actually run)

| Check | Status |
|---|---|
| All 4 scripts `py_compile` | PASS |
| Headless end-to-end (18 assertions: train→save→reload→predict→UNKNOWN→CSV→blank frame→camera) | **PASS** — test at `/tmp/opencode/test_headless.py` |
| **Real** face training + held-out recognition | **PASS 105/110** real webcam frames recognised, conf 26–40 vs limit 70 (`/tmp/opencode/real_e2e.py`) |
| **Live GUI loop** on display `:1` (window, camera, detect, recognise, A→attendance, Q→clean exit rc=0) | **PASS** (`/tmp/opencode/live_drive.py`) |

### Bugs found and fixed on 2026-09-29 (both would have broken the friend too)

1. **`train_model.py` passed Python lists to `recognizer.train()`** — OpenCV
   requires numpy arrays and hard-fails with `labels is not a numpy array`.
   Fixed: `np.array(images)`, `np.array(labels, np.int32)`.
2. **OpenCV 5.x wheels ship NO cascade XML files** — `cv2.data.haarcascades`
   is an empty directory, so the project dies with `No face cascade found`.
   `requirements.txt` now pins `opencv-contrib-python>=4.5,<5`; README has a
   troubleshooting row. Installed here: **4.14.0.94**.
3. **Docs/code mismatch (fixed):** the code writes `trainer.json`, the README
   said `labels.json`. README also claimed an LBP cascade; 4.14 ships Haar
   only, and `config.FACE_CASCADE_TRIES` already falls back to it.
4. **Trainer now auto-crops faces (`crop_face()` in `train_model.py`)** —
   added 2026-09-29 at Abdul's request so he can train on his own photo files.
   Before, a whole photo was squashed to 300×300 with the face as a small
   patch inside it. Detection uses `minSize=(60,60)` and falls back to the
   whole image when no face is found, so already-cropped captures are
   unaffected. Verified: a 480×640 photo → 67×67 face crop; the 35 existing
   tight crops pass through untouched.

## 6. CURRENT STATE

**Everything runs.** `python3 recognize_faces.py` opens the window, shows a
green box with the name, and `A` writes the attendance row.

Environment as it is now:
- `opencv-contrib-python` **4.14.0.94** in `~/.local/lib/python3.13/site-packages`
  (installed with `pip3 install --user --break-system-packages --no-deps`).
  No venv needed. Reinstall command is in the git-less history below.
- numpy 2.5.3 already present.
- Download route that works on this box: **aliyun mirror**, ~250–340 KB/s.
  `https://mirrors.aliyun.com/pypi/simple/<pkg>/` gives direct wheel URLs.
- Display: **Abdul is on `:1`** (was `:0` on 2026-09-28 — the seat now has two
  users, `abdulrehman` on `:1` and `emaan` on `:0`). Always check `who` before
  launching a GUI script.
- `python3-xlib` is installed → XTEST fake keypresses work, which is how the
  live loop was tested automatically (see `/tmp/opencode/live_drive.py`).
- `xdotool` is NOT installed and apt needs a password, so Xlib is the way.

Open question for Abdul: the auto-built `dataset/abdul/` was captured from
whoever was in front of the camera while a second user was logged in. If that
was not him, delete `dataset/` + `trainer.yml` + `trainer.json` and re-run
`capture_faces.py` himself.

**Resolved 2026-09-29 14:47:** Abdul confirmed the photos are his, and he does
**not** want his face shipped to the friend. Handover handled by exclusion, not
deletion — his working copy keeps the dataset so he can demo it.

- `~/face-recognition-for-friend.zip` — code only, 6 files, 17 KB.
  Deliberately excluded: `dataset/`, `trainer.yml`, `trainer.json`,
  `attendance/`, `team-context.md`.
- **Leak found and fixed:** the README's "your own photos" example used
  `abdul/` as a folder name. Renamed to `ali/` + `bilal/`. Always grep the
  shipped files for his name before handover — `team-context.md` is full of it
  and is the real leak risk if it is ever zipped.
- Handover copy verified by extracting it and running the whole chain from
  scratch: compiles, clear error when no dataset, trains 2 new people,
  live loop recognises both and writes attendance, exits rc=0.

### Beginner guide (2026-09-29 ~14:55)

Requested by Abdul: a Word file for the friend, who is on Windows and has
never used a terminal. Built with the `project-docs` skill (docskit
manifest → DOCX), not hand-rolled python-docx.

- `~/Face-Recognition-Beginners-Guide.docx` — 16 chapters, 12 tables, 2
  embedded diagrams, 224 KB.
- `~/Face-Recognition-Beginners-Guide.pdf` — same content, 416 KB.
- Diagram sources (editable) in `/tmp/opencode/gdocs/diagrams/*.mmd`;
  generator script `make_guide.py` is the single place to edit content —
  re-run it plus `docskit doc` to rebuild.

Audit: diagram PASS, security PASS, integrity PASS, consistency 8 PASS /
3 FAIL. The 3 FAILs are `opencv-contrib-python`, `numpy`, `LBPH` — the
analyzer reports "technologies: none detected" for a dependency-light plain
script project. All three were verified by direct source inspection
(requirements.txt:8-9, train_model.py:12, train_model.py:81), so these are
analyzer blind spots, not documentation errors. The guide also greps clean
for Abdul's name.

### Antigravity / AI-agent prompt (2026-09-29 ~15:05)

Abdul asked for a prompt an AI assistant can read and auto-run the project
with. Checked Google's official docs (antigravity.google/docs/ide/rules)
rather than guessing. Facts that shaped the design:

- `AGENTS.md` or `GEMINI.md` at project root is **`always_on`, needs no
  frontmatter**, and is read automatically. Files in `.agents/rules/*.md`
  need YAML frontmatter with a valid `trigger` and are **silently discarded**
  without it — so do not use that folder.
- **Rules files cap at 12,000 chars.** `AGENTS.md` is 8,406.
- Also works cross-tool (Cursor, Copilot, Codex, Claude Code) — a bonus.

Created `face-recognition/AGENTS.md` (added to the friend's zip) and Chapter
17 of the guide, **generated from that file** so they can never drift —
verified all 111 body lines appear in the DOCX.

Honest limit recorded in both: the assistant cannot press A/S in the live
camera window, so Phase 5 needs the human. It *can* drive the webcam for
Phase 2, and the doc says so plainly rather than overselling.

## 7. Handover notes for Abdul's friend (summary; full in README.md)

- Windows: `pip install -r requirements.txt` (must be contrib). Then
  `capture → train → recognize` in that order. ~60 photos/person, good light.
- Attendance accumulates in `attendance/YYYY-MM-DD.csv`.

## 8. Open decisions / questions

- GUIl/web/GUI upgrade? Only if Abdul asks ("do you want GUI or web instead?").
- Zip for handover: offer after demo works.
- This project is for the friend — no link to FYP/studies; do not mix contexts.

## 10. Session end 2026-09-28 — RESUME TOMORROW

**State at end of session:** wheel stuck at **16,442,447 bytes / 82,057,630**
(no growth for over an hour across several checks — the box's internet went
fully dead for large downloads). Abdul's `od.globaluni.ru` downloads **stopped**
during the session, so the pipe had room — still 0 bytes landed. Plus: the bash
tool shell was intermittently wedging on background+foreground mixes — if a new
session sees weird timeouts, run minimal commands and keep background jobs
`setsid nohup`.

**Processes still running at session end:** `fetch_cv2.sh` and `finish.sh`
(both detached; they die on reboot — `/tmp/opencode/*` is volatile).

**First thing tomorrow (new session):**
```bash
stat -c%s /tmp/opencode/cv2.whl; ls /tmp/opencode/cv2.VERIFIED /tmp/opencode/finish.DONE; tail -2 /tmp/opencode/finish.log
```
- If the size grew / VERIFIED exists → pipeline continues on its own; check
  `finish.log`, then run the live demo (section 6, "Next actions").
- If still 16,442,447 → network is still dead for it. Options to offer Abdul:
  phone hotspot for 15–20 min, or a moment when the link behaves; nothing needs
  rebuilding. If the machine **rebooted**, `/tmp` is gone → restart the wheel
  fetch from the aliyun URL in section 6 (log had last verified breakpoints;
  wheel restarts from whatever partial survived, sha256 still validates final).
- Never tell Abdul the project is "complete" until: headless test PASSED, and he
  has done the live webcam demo himself (green box + name + attendance row).

**Demo commands when ready (Abdul at the camera, display `:0`):**
```bash
echo "abdul" | DISPLAY=:0 python3 capture_faces.py   # S ~60x, then Q
python3 train_model.py
DISPLAY=:0 python3 recognize_faces.py                # A = attendance
```

**Friend handover after demo works:** offer to zip `~/face-recognition`
(README inside covers Windows setup).

## 9. Environment facts discovered this session (2026-09-28)

- LMDE 7 gigi, Debian trixie userland, GNOME, display `:0`, camera `/dev/video0`.
- External downloads: pythonhosted ~0–9 KB/s, `deb.debian.org` ~76 KB/s,
  **aliyun ~69 KB/s (only large-file route that works)**, tuna/tencent/sjtu unreachable.
- Killed pip runs leave stale locks in `/tmp/pip-build-tracker-*` → next pip hangs;
  fix: `rm -rf /tmp/pip-build-tracker-*` before retry.
- `sudo` needs a password (Abdul's not been asked for it); `pip3 install --user
  --break-system-packages` works without root (used for numpy 2.5.3; now numpy is
  in user site — do NOT need a venv).
### Handover zip + privacy audit (2026-09-29 ~15:10)

Delivered to `~/Desktop/Face-Recognition-FOR-FRIEND.zip` (8 files, 238 KB),
built from an **explicit allowlist**, never a denylist. The guide also now
lives at `~/face-recognition/Face-Recognition-Beginners-Guide.docx`.

**Trap found during the audit:** `docskit audit` had written `docs/_audit/`
into the project, and its `report.json` contained `/home/abdulrehman/...`
paths. A denylist zip would have shipped it. This is why the allowlist
matters — always enumerate what goes in, never what stays out.

Also cleaned the DOCX: set real document properties (author/title now
"Face Recognition Project", no personal data) and removed the stale
`docProps/thumbnail.jpeg` inherited from the python-docx template.

Verified absent from the zip: dataset/, trainer.yml, trainer.json,
attendance/, team-context.md, docs/, __pycache__, all .jpg. Note
**trainer.yml is a biometric face template** — it must never be handed over,
same as the photos.

Audit results: 0 identity matches across all text files and inside the DOCX
(the one hit, `C:\Users\YourName>`, is a generic placeholder in Chapter 5,
not a leak); both embedded images SHA256-match the flow diagrams, so no
photos of him; no macros/OLE/external relationships; the delivered copy
compiles, trains and predicts correctly.
