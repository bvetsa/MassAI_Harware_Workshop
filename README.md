# MassAI Model Golf

November 18, 2026 · 60 minutes · Laptop and browser

Teams shrink a neural network that distinguishes two MIT-BIH beat labels, `N` (normal beat) and `V` (premature ventricular contraction, or PVC). The ESP32 replays the same 64-value ECG windows evaluated in Python and computes each prediction in C++.

## Run the verified Wokwi demo

1. Open a [new ESP32 project](https://wokwi.com/projects/new/esp32). Paste [the sketch](wokwi/sketch.ino) and [the circuit](wokwi/diagram.json) into its `sketch.ino` and `diagram.json` tabs.
2. Press **Start the simulation**. The green LED shows predicted `N`. The red LED shows predicted `V`. The two windows repeat every four seconds.
3. Confirm both serial lines say `parity=PASS`. The logged Python value is a reference for the check. The ESP32 value and LED state come from the MLP inference code.

| Shared beat ID | MIT-BIH annotation | Python logit | Wokwi ESP32 logit | Prediction |
|---|---|---:|---:|---|
| `228:160` | N | −8.50158501 | −8.50158501 | N |
| `228:6299` | V | +4.32341528 | +4.32341528 | V |

The demo pair was selected from the practice set as the first `N` and the first `V` in record 228 that the baseline classified correctly with an absolute logit of at least 1. The pair demonstrates parity. Accuracy and sensitivity use all eligible windows in the evaluation partition.

## Run the notebooks

From a clone or downloaded source ZIP, build the student kit with Python 3.10–3.13.

```sh
python organizer/package_students.py
```

Share `dist/MassAI_Model_Golf_Student.zip` with teams. It contains both notebooks and their data bundle.

- [ECG to ESP32](01_ECG_to_ESP32.ipynb) evaluates the shipped FP32 model, plots the shared windows, builds the Wokwi project ZIP and optionally retrains the baseline.
- [Model Golf Challenge](02_Model_Golf_Challenge.ipynb) evaluates the baseline, runs width and precision trials, and exports one team-named `.mgf` submission.

In [Colab](https://colab.research.google.com/), use **File → Upload notebook** with a CPU runtime. When setup prompts for a file, choose `model-golf-data.zip`. The data bundle already contains the processed windows and pretrained model. In local Jupyter, place the data ZIP beside the notebook and use Python with NumPy and Matplotlib. The notebooks also work directly from this organizer folder.

## Score and deploy the winner

See [the facilitator runbook](materials/FACILITATOR.md) for timing, submission handling, the slide outline and fallbacks. Use `final.npz` from the separately distributed organizer kit.

```sh
python -m pip install -r requirements.txt
mkdir -p entries
python organizer/score_entries.py entries --final-data '/path/to/organizer/final.npz' --out leaderboard.csv
python organizer/deploy.py 'entries/Team Name.mgf' --out winner-wokwi
```

Put the collected team files in `entries/` before scoring, then replace `Team Name` with the first eligible team. Paste `winner-wokwi/sketch.ino` and `winner-wokwi/diagram.json` into Wokwi. The `organizer/rehearsal-wokwi/` pair is a preverified INT8 backup.

The score counts the bytes actually compiled into the firmware’s model array, including the format header, weights, biases and scales. The 80% accuracy and 94% PVC-sensitivity floors are workshop rules chosen after the organizer dry run. Eligible entries rank by bytes ascending, PVC sensitivity descending, then accuracy descending. An exact tie shares the rank.

## Data and model contract

The workshop splits recordings before slicing. Neither 201 nor 202, the two recordings from the same subject, is present. The [public data manifest](organizer/source-manifest.json) lists the training and practice records, counts and source checksums. The final split stays in the organizer kit. The task uses reference `N` and `V` beats and excludes all other symbols. [Data attribution](DATA_ATTRIBUTION.md) · [PhysioNet dataset and split guidance](https://physionet.org/content/mitdb/1.0.0/)

| Split | Recordings | N | V | Use |
|---|---:|---:|---:|---|
| Train | 11 | 23,774 | 3,997 | Fit weights on a seeded, class-balanced subset |
| Practice | 5 | 10,452 | 1,530 | Compare trials and select demo windows |
| Final | 4 | 8,889 | 687 | Score team submissions |

In the 360 Hz MLII lead, take raw sample offsets `[-63, 129)` relative to each reference annotation. Average consecutive triples, subtract the window mean, divide by the larger of its peak absolute amplitude and 0.05 mV, and store the resulting 64 values as FP32. The MLP takes those values directly, applies one ReLU hidden layer, and emits a logit. A logit ≥ 0 predicts `V`. This is a classroom exercise using pre-cut, annotated windows from selected historical recordings.

The `.mgf` format is `MGF1` followed by one byte each for hidden width and precision. INT8 adds two little-endian FP32 scales. The remaining fields, in order, are first-layer weights in hidden-neuron-major order, first-layer FP32 biases, output weights, and one FP32 output bias. Weight arrays use little-endian FP32 or signed INT8. INT8 weights are dequantized as read. Both runtimes use FP32 accumulation and activation.

## Reproduce and verify

From this folder:

```sh
# Retrain the reference and export its Wokwi files into a new folder.
python organizer/build_baseline.py --out rebuilt

# Compare native C++ and Python on every practice window for eight configurations.
python verify/host_check.py

# Independently verify the recorded Wokwi serial output against Python.
python verify/serial_check.py verify/wokwi-fp32.txt wokwi/expected.json
python verify/serial_check.py verify/wokwi-int8.txt verify/int8-expected.json

# Optional classroom data rebuild. Downloads the training and practice recordings.
python -m pip install -r organizer/requirements-data.txt
python organizer/prepare_data.py --out rebuilt --cache raw-mitdb
```

The trainer produces repeatable bytes in the tested local environment. The shipped `baseline.mgf` fixes the exact firmware reference across platforms. For an offline firmware build with an existing PlatformIO setup, run `pio run -d wokwi`. `wokwi.toml` is supplied for the Wokwi VS Code extension.

See [verification evidence](verify/VERIFICATION.md) for measured results and verification scope.
