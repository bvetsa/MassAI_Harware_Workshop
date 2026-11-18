# Beat the Bytes

**MassAI · November 18, 2026 · Laptop + Google account**

Shrink a heartbeat classifier, compare techniques, and share what you learned. The workshop has a 15-minute introduction, a 40-minute hands-on lab, and a 5-minute simulated ESP32 finale.

[**Open the Model Golf lab in Google Colab**](https://colab.research.google.com/github/bvetsa/MassAI_Harware_Workshop/blob/main/02_Model_Golf_Challenge.ipynb)

1. Sign in to Colab and use a CPU runtime. Run the setup cell. It downloads the public workshop files automatically.
2. Run **A · Baseline** to load the pretrained starter. Read the model bytes, accuracy and PVC sensitivity together.
3. Run **B · First optimization** to store the same weights in INT8. Compare the size and performance before and after.
4. In **C · Model Golf**, change only the marked width, bits, seed and training settings. Rerun that cell to add trials to the table and chart. Aim for at least **80% accuracy** and **94% PVC sensitivity** on the practice recordings.
5. In **D · Export and share**, enter a tested trial number and your team name. Download your `.mgf` and volunteer your byte count, metrics and best trick for show-and-tell.

The classifier distinguishes expert-annotated **N** (normal beat) and **V** (premature ventricular contraction, PVC) windows from MIT-BIH. It takes 64 preprocessed ECG values. Other beat labels are excluded. The practice recordings are separate from training. This educational exercise uses recorded windows and simulated hardware. [Data attribution](DATA_ATTRIBUTION.md)

## If you get stuck

- **Download failed** · Rerun setup. A presenter can supply the student ZIP. Extract it, set `manual_upload = True` in setup, and choose its `model-golf-data.zip` when prompted.
- **Name is undefined** · Run setup, then the cells above the error in order.
- **History disappeared** · Run the trial-helper cell once at the start. Rerun only the marked settings cell for each experiment.
- **Trial is below a floor** · Try a wider model or standard training and compare both metrics.
- **Export error** · Pick a number from the current trial table. Use a team name beginning with a letter or digit.

The [optional ECG to ESP32 notebook](https://colab.research.google.com/github/bvetsa/MassAI_Harware_Workshop/blob/main/01_ECG_to_ESP32.ipynb) covers inference parity, firmware export and optional baseline retraining. Both notebooks also run locally with NumPy and Matplotlib.

## Presenter demo

Open a [new Wokwi ESP32 project](https://wokwi.com/projects/new/esp32), paste [the interactive sketch](wokwi/interactive/sketch.ino) and [its diagram](wokwi/interactive/diagram.json) into the matching tabs, and start the simulation.

- Turn the dial below or above halfway to select a recorded N or PVC window. The OLED shows the selected ECG window, the LED shows the model prediction, and the serial log identifies the case and reference annotation.
- Press **B1** to toggle between the pretrained **6,346-byte baseline** and **570-byte compressed model**. B1 selects a previously trained payload. Both payloads are compiled into this demonstration.
- Look for `parity=PASS` for each selected case and model. The LEDs use the ESP32’s computed logit. The Python value is a comparison reference.

The [facilitator guide](materials/FACILITATOR.md) follows all 19 slides and gives the timing and finale handoff. The [presentation audit](materials/PRESENTATION_AUDIT.md) includes exact wording corrections for slides 5, 8, 14 and 17.

## What the bytes measure

| Model | Learned parameters | FP32 payload | INT8 payload |
|---|---:|---:|---:|
| 64 → 24 → 1 | 1,585 | 6,346 B | 1,674 B |
| 64 → 16 → 1 | 1,057 | 4,234 B | 1,122 B |
| 64 → 8 → 1 | 529 | 2,122 B | 570 B |
| 64 → 4 → 1 | 265 | 1,066 B | 294 B |

The `.mgf` payload contains architecture metadata, weights, biases and INT8 scales. INT8 stores weights in one byte, while biases and inference accumulation use FP32. Firmware also contains code and example inputs, and execution uses RAM. Model payload size, firmware flash usage and RAM usage measure different things.

## Organizer tools and offline kit

From this folder, build the manual student kit with Python 3.10–3.13.

```sh
python organizer/package_students.py
```

Share `dist/MassAI_Model_Golf_Student.zip` if the automatic download is unavailable. The ZIP has both notebooks, attribution and their offline data bundle. The download URLs in the notebooks pin public assets to commit `7241b01` and verify each file’s SHA-256. The baseline and data remain reproducible as the repository changes.

For the five-minute finale, collect a volunteered `.mgf` and export it into a fresh Wokwi replay project.

```sh
python -m pip install -r requirements.txt
python organizer/deploy.py 'entries/Team Name.mgf' --out winner-wokwi
```

Paste the generated `sketch.ino` and `diagram.json` into Wokwi and check both serial parity lines. The original [two-case replay](wokwi/sketch.ino) and [570-byte replay](organizer/rehearsal-wokwi/sketch.ino) provide prepared fallbacks. The replay diagram is alongside each sketch.

The CSV scorer remains available for optional organizer evaluation with the separate final data. It requires at least 80% accuracy and 94% PVC sensitivity, orders eligible payloads by bytes, sensitivity and accuracy, and shares exact ties. The live workshop uses practice floors and voluntary show-and-tell.

```sh
python organizer/score_entries.py entries --final-data '/path/to/organizer/final.npz' --out leaderboard.csv
```

## Reproduction and verification

```sh
python organizer/build_baseline.py --out rebuilt
python verify/host_check.py
python verify/competition_check.py
python verify/serial_check.py verify/wokwi-fp32.txt wokwi/expected.json
python verify/serial_check.py verify/wokwi-int8.txt verify/int8-expected.json
python organizer/build_interactive.py
pio run -d wokwi/interactive
```

The shared C++ inference routine implements the same MLP and zero-logit decision boundary as Python. The demo cases are `228:160` (N) and `228:6299` (V), selected from the practice set for the original parity demonstration. The model computes the output for the selected waveform.

Source preprocessing takes MLII sample offsets `[-63, 129)` at 360 Hz around each reference annotation, averages consecutive triples, centers each window, divides by the larger of its peak absolute amplitude and 0.05 mV, and stores 64 FP32 values. The [public manifest](organizer/source-manifest.json) records all training/practice IDs and source hashes. The held-out final data stays with the organizer.

To rebuild the classroom data, install `organizer/requirements-data.txt` and run `python organizer/prepare_data.py --out rebuilt --cache raw-mitdb`. See the [verification record](verify/VERIFICATION.md) for executed checks and their limits.
