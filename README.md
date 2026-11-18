# Beat the Bytes

**MassAI · November 18, 2026 · 40-minute hands-on lab**

How few bytes can your heartbeat classifier use while still catching PVCs? Experiment in teams, compare techniques, and share what you learned.

[**Open the Model Golf lab in Google Colab**](https://colab.research.google.com/github/bvetsa/MassAI_Harware_Workshop/blob/main/02_Model_Golf_Challenge.ipynb)

1. Sign in to Colab, use a CPU runtime, and run setup. The public data and pretrained model download automatically.
2. Run **A · Baseline**. Read the model bytes, accuracy and PVC sensitivity together.
3. Run **B · First optimization**. Convert the same pretrained weights from FP32 to INT8 and compare the size and performance.
4. In **C · Model Golf**, edit the marked width, bits, seed and training settings. Rerun that cell to add trials to your table and plot. Aim for at least **80% accuracy** and **94% PVC sensitivity** on the practice recordings.
5. In **D · Export and share**, enter a tested trial number and your team name. Download your `.mgf` and share your byte count, metrics and best trick.

The model distinguishes **N** (normal beat) from **V** (premature ventricular contraction, or PVC). Each example is a preprocessed window from an expert-annotated MIT-BIH beat. It takes 64 input values and uses separate recordings for training and practice. This is an educational exercise using recorded data. [Data attribution](DATA_ATTRIBUTION.md)

## If you get stuck

- **Download failed** · Rerun setup. If it keeps failing, [download the data ZIP](https://github.com/bvetsa/MassAI_Harware_Workshop/raw/refs/heads/main/model-golf-data.zip), set `manual_upload = True` in setup, and upload that ZIP when prompted.
- **Name is undefined** · Run setup, then the cells above the error in order.
- **History disappeared** · Run the trial-helper cell once at the start. Rerun only the marked settings cell for each experiment.
- **Trial is below a floor** · Try a wider model or standard training and compare both metrics.
- **Export error** · Pick a number from the current table. Start your team name with a letter or digit.

For local Jupyter, install `requirements.txt`, keep `model-golf-data.zip` beside the notebook, and run the cells in order. You can also [download the full repository](https://github.com/bvetsa/MassAI_Harware_Workshop/archive/refs/heads/main.zip) to work with the included files locally.

## What the bytes measure

| Architecture | Learned parameters | FP32 payload | INT8 payload |
|---|---:|---:|---:|
| 64 → 24 → 1 | 1,585 | 6,346 B | 1,674 B |
| 64 → 16 → 1 | 1,057 | 4,234 B | 1,122 B |
| 64 → 8 → 1 | 529 | 2,122 B | 570 B |
| 64 → 4 → 1 | 265 | 1,066 B | 294 B |

The `.mgf` payload contains architecture metadata, weights, biases and INT8 scales. INT8 stores weights in one byte, while biases and inference accumulation use FP32. The full device program also contains code and input data and uses RAM during execution.

Accuracy counts all correct predictions. PVC sensitivity counts the share of annotated PVCs the model catches. Always guessing N scores about 87% practice accuracy but catches 0% of PVCs.

## Optional · Run your model on a simulated ESP32

[**Open ECG to ESP32 in Colab**](https://colab.research.google.com/github/bvetsa/MassAI_Harware_Workshop/blob/main/01_ECG_to_ESP32.ipynb)

This notebook uses the same inputs and weights in Python and native C++ inference. It exports `baseline-wokwi.zip`. Paste its `sketch.ino` and `diagram.json` into a [new Wokwi ESP32 project](https://wokwi.com/projects/new/esp32), start the simulation, and look for `parity=PASS`. The LEDs show the model’s predictions for the two recorded example windows.

The [included sketch](wokwi/sketch.ino) and [circuit](wokwi/diagram.json) are a ready-to-run version of this exercise. The notebook also includes optional baseline retraining.
