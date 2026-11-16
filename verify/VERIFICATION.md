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
