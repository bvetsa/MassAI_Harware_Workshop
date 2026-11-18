# Beat the Bytes · Presentation alignment audit

Reviewed November 18, 2026 against all 19 slides of `Beat_the_Bytes_Workshop (1).pptx`. The supplied deck is the experience specification. The repository provides a 15-minute introduction, 40-minute guided lab and 5-minute finale.

## Required slide wording corrections

**Slide 5 · Model**

Replace “137 numbers, about 550 bytes. A chatbot model is gigabytes.” with “Our starter has 1,585 learned parameters in a 6,346-byte payload. The compact demo has 529 parameters in 570 bytes.”

For the supported MLP, the parameter count is `64h + h + h + 1 = 66h + 1`. Widths 4, 8, 16 and 24 give 265, 529, 1,057 and 1,585 parameters. None has 137 parameters. FP32 payload size is `6 + 4(66h + 1)`. INT8 payload size is `14 + 65h + 4(h + 1)`. Headers, biases and scales are counted.

**Slide 5 · Dial and B1**

Replace “our fake heart sensor. Turn it and the heartbeat on screen changes.” with “selects a preprocessed recorded N or PVC beat. Turn it to change the displayed ECG window.”

Replace “Turn the dial, watch the chip call each beat normal or abnormal. Then press B1 to shrink the model.” with “Turn the dial and watch the simulated chip classify N or PVC. Press B1 to switch between the pretrained baseline and a previously compressed model.”

The interactive Wokwi project implements the dial, waveform display, B1 model selection, actual C++ inference, LEDs and Python parity. The original replay remains available as a fallback.

**Slide 8 · Decision boundary**

Replace “score > 0 = PVC” with “score ≥ 0 = PVC”. Explain that the illustrated four-neuron network is an optimization option and that the starter has 24 hidden neurons.

**Slide 14 · Baseline**

Replace “train the starter model, note its byte size” with “load the pretrained starter, note its bytes, accuracy and PVC sensitivity”. Training smaller models happens during the optimization exercise.

**Slide 17 · Parity**

Replace “Same weights, same decisions, now in a few hundred bytes.” with “The same exported weights give matching Python and ESP32 predictions on the same recorded windows. A compact model payload can fit in a few hundred bytes.”

The 570-byte compact payload is measured. Total firmware flash and RAM include other data and code. The interactive firmware contains both model payloads, so B1 changes the active model while both remain in flash.

## Full slide audit

| Slide | Original discrepancy or check | Repository resolution / presenter cue |
|---|---|---|
| 1 | “Heartbeat monitor” can sound like a deployed medical device. | Introduce this as an educational recorded-window classifier on simulated hardware. |
| 2 | Old repository agenda and 17-minute challenge conflicted with 15/40/5. | README, notebook and facilitator guide now use the final timing. |
| 3 | Wearable examples provide motivation beyond this two-label model. | Keep as illustrative use cases. The lab demonstrates N versus PVC windows. |
| 4 | “Your heartbeat never leaves” differs from hosted Colab training. | Describe local-inference privacy as a benefit. Colab processes public recorded data. |
| 5 | Missing controls and incorrect model count. | New interactive demo plus the exact wording corrections above. |
| 6 | N versus V/PVC agrees with labels. | Preserve expert annotations and exclusions. Avoid generalizing to all abnormalities. |
| 7 | Weighted sum agrees with inference. | No functional correction needed. |
| 8 | Four-neuron picture differs from starter width; strict inequality differs from firmware. | Explain supported widths and use ≥ 0. |
| 9 | Always-N score about 87% is correct for the practice set. | Notebook reports 87.2% accuracy and 0% sensitivity plus confusion counts. |
| 10 | FP32-to-INT8 approximately 4× smaller can overlook biases/scales. | Show measured 6,346 → 1,674 bytes (73.6% saved). Training choices stay limited. |
| 11 | Formal competition language conflicted with “No winners”. | Student materials now emphasize personal/team experiments and voluntary sharing. Optional scorer retained. |
| 12 | Open-ended experimentation fits the available model family. | Four widths, two precisions, three seeds and two durations remain supported. |
| 13 | Manual packaging/upload obstructed entry. | Prominent Colab link with direct, checksum-verified public downloads. Manual ZIP remains a fallback. |
| 14 | Training starter conflicted with immediate pretrained result. | Load the starter first, then train narrower models. Export prints the exact configuration. |
| 15 | Recovery and optimization advice needed matching notebook cues. | Helpful errors, marked editable settings, run-order guidance and history-reset note. |
| 16 | Show-and-tell conflicted with declared winners. | Five minutes of voluntary sharing in the lab agenda. |
| 17 | Arbitrary exported model needs a safe five-minute handoff. | Existing exporter creates native C++ replay project. Prepared compact replay available. |
| 18 | Trust and errors require honest evaluation limits. | Discuss new-patient/device tests, both error types and the limits of two shared cases. |
| 19 | Optional follow-up should remain accessible. | Notebook 01 also downloads its assets automatically. Physical hardware execution remains unverified. |

[Facilitator walkthrough](FACILITATOR.md) · [Executed checks and limitations](../verify/VERIFICATION.md)
