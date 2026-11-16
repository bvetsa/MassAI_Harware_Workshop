# Model Golf student kit

**MassAI · November 18, 2026**

1. Extract this kit and open `02_Model_Golf_Challenge.ipynb` in [Google Colab](https://colab.research.google.com/) via **File → Upload notebook**.
2. Run the setup cell on the CPU runtime. Select `model-golf-data.zip` when prompted. Keep the ZIP intact.
3. Run **A · Baseline** and **B · First optimization**. Compare the pretrained model with the INT8 version before training a model of your own.
4. In **C · Model Golf**, rerun the trial cell with different widths and weight precision. Try changing the seed or training length if you have time. Use the practice table and plot to choose a trial.
5. In **D · Submit**, enter the trial number and your team name. Download your `.mgf` and give the facilitator one file per team by minute 37.

The organizer scores submissions on separate recordings. The final floors are **80% accuracy** and **94% PVC sensitivity**. The smallest qualifying payload wins. Ties use sensitivity, then accuracy. An exact tie shares the rank.

Use `01_ECG_to_ESP32.ipynb` for the optional full demo. It creates the sketch and circuit files and shows the Python predictions to compare in Wokwi.

Each input is a window around an annotated MIT-BIH ECG beat. `N` is a normal beat. `V` is a premature ventricular contraction (PVC). This exercise uses pre-cut windows and two annotation codes. [MIT-BIH dataset](https://doi.org/10.13026/C2F305) · [WFDB beat codes](https://physionet.org/physiotools/wpg/wpg_36.htm)
