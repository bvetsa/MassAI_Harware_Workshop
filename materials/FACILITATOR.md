# Beat the Bytes · Facilitator guide

November 18, 2026 · Junaid Pathan and Bhargava · 60 minutes

This guide follows the 19 slides in `Beat_the_Bytes_Workshop (1).pptx`. Use the wording corrections in [the presentation audit](PRESENTATION_AUDIT.md) before presenting.

## Timing

| Session time | Activity | Presenter cue |
|---|---|---|
| 0–15 | Introduction, slides 1–12 | Keep slide 5’s prepared demo to about 90 seconds. Explain N/PVC, width, quantization and both metrics. |
| 15–20 | Slide 13, setup | Have everyone open the README’s Colab link, sign in, select CPU and run setup. Downloads are automatic. |
| 20–25 | Slide 14, Stage A | Load the pretrained starter, record its size and inspect confusion counts. |
| 25–30 | Slide 14, Stage B | Convert the same weights to INT8. Ask students to predict the byte reduction before running it. |
| 30–45 | Slides 14–15, Stage C | Try widths and precision first. Offer seed/training variation to faster teams. Troubleshoot in pairs. |
| 45–50 | Slide 14, Stage D | Teams choose a trial and export `.mgf`. Collect one volunteered model for the finale. |
| 50–55 | Slide 16 | Invite two or three teams to share bytes, both metrics, and one change that helped. Prepare the volunteered firmware in parallel. |
| 55–60 | Slides 17–19 | Run the exported model, compare both parity lines, ask one discussion question and close. |

If onboarding takes longer, use the prepared baseline on the projector while helping students connect, and shorten optional seed experiments. The required first compression exercise uses pretrained weights.

## Slide cues

| Slide | Cue and audience action | Demo or fallback |
|---|---|---|
| 1 · Beat the Bytes | Introduce an educational classifier using real recorded beats and simulated hardware. | No medical-device performance claim. |
| 2 · Today’s plan | State the 15/40/5 timing and confirm laptop + Google account. | A pair can share a browser if needed. |
| 3 · AI on your body | Use wearables as motivation. Ask for a familiar example. | The lab models two beat annotations. |
| 4 · Cloud tradeoffs | Explain that local inference can work offline. Our public-data training lab runs in hosted Colab. | The Wokwi firmware has no network code. |
| 5 · Meet our chip | Turn the dial N → PVC, point to the waveform, LED and serial prediction. Press B1 and point to 6,346 → 570 bytes. | Say B1 selects a precompressed model. If simulation is unavailable, use the verification screenshot and replay logs. |
| 6 · Our patient | Identify N as normal and V as PVC. | The dial chooses two recorded windows, with their original MIT-BIH IDs. |
| 7 · Weighted score | Ask which input gets the largest weight in the example. | Weights are learned from the training partition. |
| 8 · A model | Use the four-neuron diagram as one supported width. The starter has 24 hidden neurons. | Say score ≥ 0 predicts PVC. |
| 9 · Two mistakes | Ask what an always-N predictor misses. | The practice set’s always-N score is 87.2% accuracy and 0% PVC sensitivity. |
| 10 · Shrinking | Introduce width first, then stored precision. | INT8 biases and arithmetic stay FP32. |
| 11 · Mission | Keep 80% accuracy and 94% sensitivity together. | Use practice floors for show-and-tell. |
| 12 · Ready | Ask teams to choose a driver and a reader. | Swap roles during Stage C. |
| 13 · Repository | Open the prominent Colab link, sign in and run setup. | Automatic pinned downloads, then manual ZIP fallback if needed. |
| 14 · Lab | Load the starter, quantize, try smaller widths, export. | Keep this slide visible through the lab. |
| 15 · Stuck | Change one setting, try wider/standard, rerun setup and cells in order for missing variables. | A presenter can run a shared notebook if a pair is blocked. |
| 16 · Show and tell | Ask what changed, bytes reached, and what happened to PVC sensitivity. | Invite voluntary sharing. |
| 17 · Finale | Run a volunteered `.mgf`, check identity and both parity lines. | Use the 570-byte prepared replay if the handoff is delayed, and name it as the rehearsal model. |
| 18 · Discussion | Pick one question if time is short. Ask what evidence would be needed before patient use. | Matching Python proves implementation agreement on these cases. Evaluation across new patients/devices is a separate question. |
| 19 · Continue | Point to notebook 01 and the repository. | Hardware execution beyond Wokwi remains a follow-up. |

## Prepare the opening demo

1. Open [a new ESP32 Wokwi project](https://wokwi.com/projects/new/esp32). Paste `wokwi/interactive/sketch.ino` and `wokwi/interactive/diagram.json` into the matching tabs. Start the simulation before the talk. Both use the built-in Arduino core and Wire library.
2. Keep the serial monitor visible. Dial below halfway selects `228:160` (annotated N). Dial above halfway selects `228:6299` (annotated V). The OLED draws the selected normalized waveform. The LED uses the computed class, green for N and red for V.
3. Press B1 once to select the compact model. Press it again to return to the baseline. Confirm `MODEL active=... bytes=...` and `parity=PASS` after each change. The model fingerprint identifies the exact payload.
4. Keep `wokwi/sketch.ino` and `wokwi/diagram.json` ready as the original two-case replay. `verify/wokwi-fp32.txt`, `verify/wokwi-int8.txt` and their screenshots provide offline evidence if the service is unavailable.

The dial selects discrete stored cases. Both trained model payloads are in the demo firmware, so selecting the smaller model changes the active payload while the whole firmware still contains both. There is no patient input, on-device training or on-device quantization.

## Prepare the closing finale

Before the event, install `requirements.txt` in the organizer’s Python environment. During export, have a volunteer send a `.mgf` through the channel you announce in the room. Save it as `entries/Team Name.mgf`.

```sh
python organizer/deploy.py 'entries/Team Name.mgf' --out winner-wokwi
```

The output folder name is an existing tool convention. This is a volunteered demonstration. Paste its `sketch.ino` and `diagram.json` into a second prepared Wokwi tab. Start, read its payload size, and check both predictions against the Python references in `expected.json`. This exported model uses the original replay circuit. A prediction may disagree with the dataset annotation while parity still passes. Explain the two comparisons.

If the handoff is delayed, use `organizer/rehearsal-wokwi/` and state that it is the prepared 570-byte model. The optional CSV scorer stays available for later evaluation on the separate final dataset. It is outside the live show-and-tell workflow.

## Before attendees arrive

- Open the actual README link and check that setup completes on the venue Wi-Fi in a signed-in Colab CPU session. Run A, B, one trial and an export. Keep the manual student ZIP locally.
- Start Wokwi, turn the dial both ways, press and release B1, and check waveform, LEDs and four parity combinations.
- Apply the four slide wording corrections. Confirm the projector can show the Colab plot and serial log legibly.
- Agree on a simple file collection channel and which presenter operates the finale. Stage the prepared replay backup.
