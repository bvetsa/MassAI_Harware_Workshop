# ECG data attribution

`classroom.npz`, `demo_cases.npz`, and `organizer/final.npz` contain processed waveform windows and reference labels from George Moody and Roger Mark’s MIT-BIH Arrhythmia Database, version 1.0.0, published by PhysioNet in 2005. The original database is available under the Open Data Commons Attribution License v1.0. [Dataset and citation](https://doi.org/10.13026/C2F305) · [License](https://opendatacommons.org/licenses/by/1-0/)

The original study is Moody GB and Mark RG, *The impact of the MIT-BIH Arrhythmia Database*, IEEE Engineering in Medicine and Biology, 20(3), 45–50, 2001. [Publication](https://pubmed.ncbi.nlm.nih.gov/11446209/)

The workshop derives 64-value windows from the MLII lead at reference annotations `N` and `V`. It changes waveform values through block averaging and per-window normalization and retains the annotation class, record ID and original annotated sample number. Training uses records 100, 106, 114, 116, 119, 200, 203, 213, 215, 221, and 233. Practice uses records 105, 205, 208, 219, and 228. Two selected windows from record 228 are embedded in the simulation. [Annotation codes](https://physionet.org/physiotools/wpg/wpg_36.htm) · [Database record directory](https://physionet.org/files/mitdb/1.0.0/mitdbdir/records.htm)
