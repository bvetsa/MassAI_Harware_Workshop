#include <fstream>
#include <iomanip>
#include <iostream>
#include <iterator>
#include <limits>
#include <vector>
#include "inference.h"

int main(int argc, char **argv) {
  if (argc != 3) return 1;
  std::ifstream weights(argv[1], std::ios::binary);
  std::ifstream input(argv[2], std::ios::binary);
  if (!weights || !input) return 2;
  const std::vector<uint8_t> model{std::istreambuf_iterator<char>(weights), {}};
  float samples[kInputs];
  std::cout << std::setprecision(std::numeric_limits<float>::max_digits10);
  while (input.read(reinterpret_cast<char *>(samples), sizeof(samples))) {
    const float z = predict(model.data(), model.size(), samples);
    if (!isfinite(z)) return 3;
    std::cout << z << '\n';
  }
  return input.eof() && input.gcount() == 0 ? 0 : 4;
}
