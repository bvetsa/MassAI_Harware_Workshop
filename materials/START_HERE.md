# Beat the Bytes · Start here

**MassAI · November 18, 2026 · 40-minute lab**

[**Open the lab in Google Colab**](https://colab.research.google.com/github/bvetsa/MassAI_Harware_Workshop/blob/main/02_Model_Golf_Challenge.ipynb)

1. Sign in with your Google account. Use the CPU runtime and run setup. The public workshop files download automatically.
2. Run **A · Baseline** and **B · First optimization**. Compare the pretrained FP32 model with the INT8 version before training your own smaller model.
3. In **C · Model Golf**, edit only the four marked settings. Change one thing at a time and rerun that cell. Compare model bytes, accuracy and PVC sensitivity in the table and plot.
4. In **D · Export and share**, choose a trial number and team name. Download your `.mgf` and volunteer your size, metrics and best technique for show-and-tell.

Aim for **80% accuracy** and **94% PVC sensitivity** on the practice recordings, then see how small you can go. Keep both metrics visible. A missed PVC is a false negative. A normal beat flagged as PVC is a false positive.

**Manual fallback** · If setup cannot download, rerun it first. With the presenter’s student kit, set `manual_upload = True` in setup and choose `model-golf-data.zip`. For local Jupyter, keep that ZIP beside the notebook. Rerun setup and the following cells in order if variables are missing. Run the trial helper once, then rerun only the experiment settings cell to keep your history.

The optional `01_ECG_to_ESP32.ipynb` shows how Python and the ESP32 use the same inputs and weights. Each input is a preprocessed window around an expert-annotated MIT-BIH beat. N is a normal beat and V is a PVC. [MIT-BIH dataset](https://doi.org/10.13026/C2F305) · [Beat codes](https://physionet.org/physiotools/wpg/wpg_36.htm)
