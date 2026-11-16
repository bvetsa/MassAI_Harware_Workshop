# Model Golf facilitator runbook

**Wednesday, November 18, 2026 · 60 minutes · Mixed technical audience**

At the end, teams should be able to explain what they compressed, show the actual model bytes, and explain a false negative and a false positive in this two-label task.

## Run of show

| Minutes | Lead | Participants |
|---|---|---|
| 0–8 | Start the FP32 Wokwi demo. Show the waveform pair and ask what lights each LED. Point to both serial predictions and `parity=PASS`. | Predict what changes when the ECG window changes. |
| 8–15 | Define model width, storage precision, model bytes, accuracy and PVC sensitivity. | Explain how an always-normal classifier can achieve high accuracy while missing every PVC. |
| 15–20 | Share the student ZIP. Demonstrate notebook upload and load its data ZIP. Show the 6,346-byte baseline result. | Form teams of 2–3, start CPU Colab, run setup and the baseline. |
| 20–37 | Keep the challenge instructions visible. At minute 32, call five minutes to submission. | Try width 24 at INT8, then adjust width and precision. Choose and export one entry. |
| 37–40 | Freeze entries. Run scoring. Open the CSV full screen and identify the first-place eligible entry. | Compare the submitted size and the scored metrics. |
| 40–50 | Export the winner and start Wokwi. Identify the model by bytes and compare both logit lines with `expected.json`. | Compare predictions with the baseline and explain why matching implementations can still make a wrong classification. |
| 50–60 | Discuss a recording-level failure from the organizer rehearsal. Discuss the limits of using pre-cut beats, class imbalance and new patients or devices. | Propose an evaluation that better exposes false alarms and missed PVCs. |

## Slide structure

1. **Model Golf** · “How small can we make a heartbeat classifier?” Open Wokwi after the first audience prediction.
2. **What the model sees** · Use `ecg-windows.png` or the baseline notebook plot. Define `N` and PVC. Point out that each window is aligned to a reference annotation and spans roughly half a second.
3. **How models get smaller** · Draw `64 samples → ReLU hidden layer → one logit`. Fewer hidden neurons remove weights. INT8 weight storage replaces each FP32 weight with a byte and adds two scales. Activations and biases stay FP32.
4. **Two ways to make a mistake** · Mark a missed PVC as a false negative and a normal beat flagged as PVC as a false positive. Accuracy uses all examples. Sensitivity uses only annotated PVCs.
5. **Your turn** · Put the student ZIP and the chosen submission channel on screen. Keep `width`, `bits`, 80% accuracy, 94% PVC sensitivity and minute 37 visible during the lab.
6. **Leaderboard and live deployment** · Screen-share the real CSV and Wokwi. Explain byte count, qualification and the tie-breaker. The firmware computes the logits and drives the LEDs.
7. **Where the model struggled** · Share the aggregate and per-record results from the organizer rehearsal after submissions close. Ask what a pooled score hides.

## Demo and scoring cues

- Opening demo uses `wokwi/sketch.ino` and `wokwi/diagram.json`. Preload the two browser tabs before participants arrive. Normal fixture `228:160` predicts `N` and PVC fixture `228:6299` predicts `V` in the baseline. Both inference comparisons pass at absolute tolerance 0.00001.
- Have teams send one `.mgf` using the workshop’s collection channel. Save each as `entries/Team Name.mgf`. Use one consistent filename per team and overwrite an earlier submission only if the team sends a replacement before the cutoff. Keep the facilitator’s final window data with the organizer.
- Run `python organizer/score_entries.py entries --final-data "/path/to/organizer/final.npz" --out leaderboard.csv` with the final data from your local organizer kit. Show rank, team, bytes, accuracy, PVC sensitivity and eligibility on the projector. The CSV also has confusion counts and the payload fingerprint. Exact ties share rank. Pick one tied entry for the live demo if time permits only one.
- Run `python organizer/deploy.py 'entries/Team Name.mgf' --out winner-wokwi`. Copy its two browser files into a new Wokwi ESP32 project and start. If an example is classified differently from its dataset annotation and parity still passes, show that distinction explicitly.
- If Wokwi is unavailable, show the pre-recorded screenshots and serial logs in `verify/` while running the Python notebook locally. If the winning model misses the live demo window or no entry qualifies, use `organizer/rehearsal-wokwi/` and call it the 570-byte rehearsal model. If students cannot start Colab, use a single instructor notebook and have teams predict and record the result of each trial before you run it.

## Remaining preparation

**Monday, November 16**

- Open the verified baseline in the browser you will present from. Familiarize yourself with the two serial lines and the replay timing. Save local copies of both verification screenshots.
- Decide how teams will hand over files and designate the person running the leaderboard. Create an empty `entries/` folder and practice collecting one small file.

**Tuesday, November 17**

- From a fresh Colab session, upload the actual student notebook and ZIP. Try width 8, export a named `.mgf`, score it, generate the Wokwi sketch, and paste it into a fresh simulator. Test the student sharing link with an account outside the organizer team if available.
- Rehearse the 37–50 minute handoff against a timer. Stage the baseline and rehearsal sketch files locally. Put the student kit link and collection instructions on slide 5 before sharing it.

**Wednesday, November 18, before doors open**

- Check venue Wi-Fi and open Colab, Wokwi and the presenter materials. Verify the green and red LEDs and both parity lines. Decide which tab stays on the projector during the lab.
