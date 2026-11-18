#include <Arduino.h>
#include <Wire.h>
#include "inference.h"
#include "model_data.h"
#include "demo_data.h"

constexpr int kNormalLed = 18;
constexpr int kPvcLed = 19;
constexpr int kDial = 34;
constexpr int kButton = 23;
bool compressed = false;
size_t selected = 0;

void displayBeat(const float *samples) {
  uint8_t pixels[1024] = {};
  int previousY = 32 - int(samples[0] * 28);
  for (size_t i = 0; i < kInputs; ++i) {
    const int y = 32 - int(samples[i] * 28);
    const int start = y < previousY ? y : previousY;
    const int end = y > previousY ? y : previousY;
    for (int row = start; row <= end; ++row) {
      pixels[(row / 8) * 128 + i * 2] |= uint8_t(1 << (row % 8));
      pixels[(row / 8) * 128 + i * 2 + 1] |= uint8_t(1 << (row % 8));
    }
    previousY = y;
  }
  // SSD1306 horizontal addressing, all 128 columns and eight display pages.
  Wire.beginTransmission(0x3c);
  const uint8_t window[] = {0x00, 0x21, 0, 127, 0x22, 0, 7};
  Wire.write(window, sizeof(window));
  Wire.endTransmission();
  for (size_t offset = 0; offset < sizeof(pixels); offset += 16) {
    Wire.beginTransmission(0x3c);
    Wire.write(0x40);
    Wire.write(pixels + offset, 16);
    Wire.endTransmission();
  }
}

void reportSelection() {
  const uint8_t *model = compressed ? compact::kModel : baseline::kModel;
  const size_t bytes = compressed ? sizeof(compact::kModel) : sizeof(baseline::kModel);
  const char *digest = compressed ? compact::kModelSha256 : baseline::kModelSha256;
  const char *name = compressed ? "compact" : "baseline";
  const DemoCase &beat = kDemoCases[selected];
  const float reference = compressed ? kCompactLogits[selected] : beat.pythonLogit;
  const float z = predict(model, bytes, beat.samples);
  digitalWrite(kNormalLed, isfinite(z) && z < 0 ? HIGH : LOW);
  digitalWrite(kPvcLed, isfinite(z) && z >= 0 ? HIGH : LOW);
  Serial.printf("MODEL active=%s bytes=%u sha256=%s\n", name, unsigned(bytes), digest);
  Serial.printf("BEAT %s annotation=%c esp32=%.8f python=%.8f predicted=%c parity=%s\n",
                beat.id, beat.annotation ? 'V' : 'N', double(z), double(reference),
                isfinite(z) ? (z >= 0 ? 'V' : 'N') : '?', matchesPython(z, reference) ? "PASS" : "FAIL");
  displayBeat(beat.samples);
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  pinMode(kNormalLed, OUTPUT);
  pinMode(kPvcLed, OUTPUT);
  pinMode(kButton, INPUT_PULLUP);
  Wire.begin(21, 22);
  Wire.beginTransmission(0x3c);
  const uint8_t init[] = {0x00, 0xae, 0xd5, 0x80, 0xa8, 0x3f, 0xd3, 0x00, 0x40,
                          0x8d, 0x14, 0x20, 0x00, 0xa1, 0xc8, 0xda, 0x12, 0x81,
                          0xcf, 0xd9, 0xf1, 0xdb, 0x40, 0xa4, 0xa6, 0xaf};
  Wire.write(init, sizeof(init));
  Wire.endTransmission();
  selected = analogRead(kDial) >= 2048 ? 1 : 0;
  Serial.println("Dial selects recorded N/PVC windows on the display. B1 selects a precompressed model.");
  reportSelection();
}

void loop() {
  // Hysteresis prevents an unstable selection when the dial is near halfway.
  const int dial = analogRead(kDial);
  const size_t nextCase = dial > 2200 ? 1 : (dial < 1900 ? 0 : selected);
  bool changed = nextCase != selected;
  selected = nextCase;

  static int lastReading = HIGH;
  static int stableButton = HIGH;
  static unsigned long edgeTime = 0;
  const int reading = digitalRead(kButton);
  if (reading != lastReading) edgeTime = millis();
  lastReading = reading;
  if (millis() - edgeTime >= 30 && reading != stableButton) {
    stableButton = reading;
    if (stableButton == LOW) {
      compressed = !compressed;
      changed = true;
    }
  }
  if (changed) reportSelection();

  delay(8);
}
