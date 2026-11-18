# Verification record

- **Data provenance** · Checked all 49,329 original workshop labels directly against the PhysioNet `.atr` files and verified that no recording crosses partitions. `organizer/source-manifest.json` records the training and practice counts, IDs and source checksums. The final partition stays in the organizer kit.
- **Reference training** · Repeated the NumPy 2.2.6 training run locally. The rebuilt `baseline.mgf` was byte-identical to the shipped 6,346-byte model.
- **Desktop C++ parity** · Compared the firmware’s native inference routine with the Python implementation on all 11,982 practice windows for each of the eight supported width and precision combinations. All 95,856 predictions and logits matched exactly in this run.
- **ESP32 compile** · Built the split source using PlatformIO ESP32 platform 7.1.3 and the Arduino framework.
- **Wokwi execution** · Ran the generated browser sketch in Wokwi on `board-esp32-devkit-c-v4` for the 6,346-byte FP32 baseline and the 570-byte INT8 rehearsal model. Both matched Python’s class and logit for both shared inputs at `1e-5` absolute tolerance. Watched the green and red prediction LEDs during simulation. The text files contain the observed boot identity and one serial line per fixture. The screenshots show the running simulator.
- **Notebook execution** · Started both notebooks from the data ZIP in local Jupyter. The baseline exported the demo and retrained the reference. The challenge ran both quantization and width reduction and wrote a 570-byte team submission.
- **Scorer** · Ran six dry-run entries. The scorer recorded shared first place for two identical eligible payloads, rejected an entry below the sensitivity floor, and reported a malformed header without interrupting ranking.

## Milestone 2 competition

- Ran both notebooks in fresh local Jupyter kernels from the student ZIP. `python verify/competition_check.py` exercises all 48 width, precision, seed and training combinations, cache reuse, the rendered plot, and valid and invalid submissions. The scorer integration uses the practice data as a fixture. The final recordings were unused in this milestone.
- Exported a 570-byte submission from the challenge notebook using width 8, INT8, seed 7 and short training. PlatformIO compiled it, and Wokwi returned `parity=PASS` for both shared windows. The simulated ESP32 reported logits of −6.77228785 and +2.03583574, matching Python within `1e-5`.
- Reran the Milestone 1 desktop C++ and reference serial checks. Default training reproduced the shipped model and browser sketch byte for byte on the tested NumPy version.

## Verification scope

The Wokwi runs use pre-extracted ECG windows. Full practice-set parity was tested on a desktop with the same inference code. The notebooks were exercised in a local Jupyter runtime. Hosted Colab upload/download controls, the Wokwi VS Code extension, physical ESP32 hardware, and the merged binary file picker are outside the verified path. Competition entries will need their own final scores and Wokwi run.

## November 18 · Final workshop audit

The final source was checked against all 19 slides of `Beat_the_Bytes_Workshop (1).pptx`. See [the slide audit](../materials/PRESENTATION_AUDIT.md) for the required wording changes and the 15/40/5 guide.

| Check actually executed | Result |
|---|---|
| Automatic notebook setup in an empty directory | Downloaded the pinned public lab assets and verified their SHA-256 hashes. Setup, baseline and first INT8 conversion completed in 1.24 seconds in this laptop run. |
| Both notebooks from the actual student ZIP | Fresh local Jupyter kernels ran all cells, including retraining in notebook 01 and an exported 1,122-byte model from notebook 02. |
| Both notebooks with automatic downloads | Fresh local Jupyter kernels ran the remote data path and all cells. Notebook 02 completed in 1.81 seconds including kernel startup. Its first training/scoring/plot cell took 0.23 seconds. |
| Milestone 2 test | All 48 width/precision/seed/duration trials, cache reuse, plot, invalid submissions, scorer and deployment export passed. Median standard training was 0.103 seconds and short training 0.040 seconds. |
| Milestone 1 checks | All eight width/precision configurations matched native C++ on every practice window. Both recorded replay serial checks passed. Retrained baseline bytes and generated replay sketch remained identical to the original. |
| Interactive ESP32 firmware | PlatformIO compiled the final project. Reported static RAM 21,992 bytes and flash usage 300,397 bytes for this build. These are build figures for the whole demo, separate from either model payload. |
| Actual interactive Wokwi execution | Turned the dial to both recorded cases, pressed and released B1, and switched back. OLED waveform and green/red LEDs changed. Baseline and compact model logits matched Python for all four case/model combinations. |
| Saved interactive evidence | `interactive-normal.jpg`, `interactive-pvc.jpg` and `interactive-serial.txt` capture the observed run. `python verify/interactive_check.py` rechecks model hashes, sizes, labels and logits from that log. |

The final demo's baseline logits were −8.50158501 (N) and +4.32341528 (V). Compact logits were −6.61995602 (N) and +4.46503210 (V). The absolute parity tolerance is 0.00001.

The available browser opened Colab, but Connect displayed **Google sign-in required**. Hosted CPU execution and the browser's `.mgf` download remain unverified. Computation timings come from local execution and do not measure participant reading time, Google sign-in or venue Wi-Fi. The 40-minute schedule allocates five minutes to setup, five each to baseline and INT8, 15 to trials, five to export, and five to sharing. A first-time participant rehearsal remains a presenter pre-event check.
