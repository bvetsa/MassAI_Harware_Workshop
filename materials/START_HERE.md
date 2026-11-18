# Beat the Bytes · Start here

[**Open the lab in Google Colab**](https://colab.research.google.com/github/bvetsa/MassAI_Harware_Workshop/blob/main/02_Model_Golf_Challenge.ipynb)

1. Sign in, use a CPU runtime, and run setup. The public workshop files download automatically.
2. Run **A · Baseline** and **B · First optimization**. Compare the pretrained FP32 model with the INT8 version.
3. In **C · Model Golf**, edit only the four marked settings. Change one thing at a time and rerun that cell. Compare bytes, accuracy and PVC sensitivity in the table and plot.
4. In **D · Export and share**, choose a trial number and team name. Download your `.mgf` and share your size, metrics and best technique.

Aim for **80% accuracy** and **94% PVC sensitivity** on the practice recordings. A missed PVC is a false negative. A normal beat flagged as PVC is a false positive.

If setup cannot download, [download the data ZIP](https://github.com/bvetsa/MassAI_Harware_Workshop/raw/refs/heads/main/model-golf-data.zip), set `manual_upload = True`, and select the ZIP when prompted. For local Jupyter, keep it beside the notebook. Run the trial helper once, then rerun the experiment settings cell to keep your history.

The optional [ECG to ESP32 notebook](https://colab.research.google.com/github/bvetsa/MassAI_Harware_Workshop/blob/main/01_ECG_to_ESP32.ipynb) shows how Python and a simulated ESP32 use the same inputs and weights.
