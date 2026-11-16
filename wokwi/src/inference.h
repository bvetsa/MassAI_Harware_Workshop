#pragma once
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

constexpr size_t kInputs = 64;
constexpr float kTolerance = 0.00001f;
static_assert(sizeof(float) == 4, "Model Golf requires IEEE binary32 floats");

struct DemoCase {
  const char *id;
  int annotation;
  float pythonLogit;
  float samples[kInputs];
};

inline float readFloat(const uint8_t *bytes) {
  uint32_t bits = uint32_t(bytes[0]) | (uint32_t(bytes[1]) << 8) |
                  (uint32_t(bytes[2]) << 16) | (uint32_t(bytes[3]) << 24);
  float value;
  memcpy(&value, &bits, sizeof(value));
  return value;
}

inline float readWeight(const uint8_t *bytes, bool int8, float scale) {
  if (!int8) return readFloat(bytes);
  const int signedValue = bytes[0] < 128 ? bytes[0] : int(bytes[0]) - 256;
  return float(signedValue) * scale;
}

inline float multiplyAdd(float sum, float value, float weight) {
  // Round the product before adding, as in the Python reference.
  volatile float product = value * weight;
  return sum + product;
}

inline float predict(const uint8_t *model, size_t bytes, const float *input) {
  constexpr size_t header = 6;
  if (bytes < header || memcmp(model, "MGF1", 4) != 0) return NAN;
  const size_t width = model[4];
  const bool int8 = model[5] == 8;
  if (width != 4 && width != 8 && width != 16 && width != 24) return NAN;
  if (!int8 && model[5] != 32) return NAN;
  const size_t stride = int8 ? 1 : 4;
  const size_t scaleBytes = int8 ? 8 : 0;
  if (bytes != header + scaleBytes + (kInputs + 1) * width * stride + 4 * (width + 1)) return NAN;

  const float s1 = int8 ? readFloat(model + header) : 1.0f;
  const float s2 = int8 ? readFloat(model + header + 4) : 1.0f;
  const uint8_t *w1 = model + header + scaleBytes;
  const uint8_t *b1 = w1 + width * kInputs * stride;
  const uint8_t *w2 = b1 + width * 4;
  float logit = readFloat(w2 + width * stride);
  for (size_t j = 0; j < width; ++j) {
    float hidden = readFloat(b1 + j * 4);
    for (size_t i = 0; i < kInputs; ++i) {
      const float weight = readWeight(w1 + (j * kInputs + i) * stride, int8, s1);
      hidden = multiplyAdd(hidden, input[i], weight);
    }
    const float outputWeight = readWeight(w2 + j * stride, int8, s2);
    logit = multiplyAdd(logit, hidden > 0.0f ? hidden : 0.0f, outputWeight);
  }
  return logit;
}

inline bool matchesPython(float z, float reference) {
  return isfinite(z) && fabsf(z - reference) <= kTolerance && (z >= 0) == (reference >= 0);
}
