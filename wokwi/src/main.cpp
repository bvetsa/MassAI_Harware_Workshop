#include <Arduino.h>
#include "inference.h"
#include "model_data.h"
#include "demo_data.h"

constexpr int kNormalLed = 18;
constexpr int kPvcLed = 19;

void setup() {
  Serial.begin(115200);
  pinMode(kNormalLed, OUTPUT);
  pinMode(kPvcLed, OUTPUT);
  Serial.printf("MODEL bytes=%u sha256=%s\n", unsigned(sizeof(kModel)), kModelSha256);
}

void loop() {
  static size_t index = 0;
  const DemoCase &beat = kDemoCases[index];
  const float z = predict(kModel, sizeof(kModel), beat.samples);
  const bool valid = isfinite(z);
  const bool pvc = z >= 0;
  digitalWrite(kNormalLed, valid && !pvc ? HIGH : LOW);
  digitalWrite(kPvcLed, valid && pvc ? HIGH : LOW);
  Serial.printf("BEAT %s annotation=%c esp32=%.8f python=%.8f predicted=%c parity=%s\n",
                beat.id, beat.annotation ? 'V' : 'N', double(z), double(beat.pythonLogit),
                valid ? (pvc ? 'V' : 'N') : '?', matchesPython(z, beat.pythonLogit) ? "PASS" : "FAIL");
  index = (index + 1) % (sizeof(kDemoCases) / sizeof(kDemoCases[0]));
  delay(2000);
}
