#  Design & Functional Simulation of Shor’s Order- Finding Algorithm for Small-Scale Integers

## Teammates-
1) Adhway Sharma
2) Vishwambhara R Bhagawath
3) K Thejas

## 📌 Table of Contents
- [Overview](#-overview)
- [Objective](#-obejctive)
- [Methodology](#-methodology)
- [Virtal Environment Setup](#-virtual-environment-setup)

---

## 📖 Overview
Quantum computing is an emerging field of computing that uses the principles of quantum mechanics to solve certain computational problems more efficiently than conventional computers. One of the important applications of quantum computing is integer factorization, which involves finding the prime factors of a given integer.

## 🔬 Objective
The objectives are listed as follows: 
1) To design and simulate Shor’s order-finding algorithm for small-scale integers.
2) To implement quantum operations such as superposition, modular exponentiation, and QFT to estimate the order.
3) To use classical GCD-based processing to obtain the factors from the estimated order.
4) To evaluate the functional correctness of the algorithm through quantum simulation.

## 📌 Methodology
1) Phase 1(Input Validation)- Read N and a, validate inputs, check gcd(a,N)=1.
2) Phase 2(Classical Baseline)- Calculate modular powers and the reference order r.
3) Phase 3(Circuit Design)- Create quantum registers, superposition, controlled modular multiplication, and inverse Quantum Fourier Transform(QFT).
4) Phase 4(Quantum Simulation)- Transpile the circuit for Aer, execute the configured number of shots, and collect measurement counts.
5) Phase 5(Order Estimation)- Convert measurement outcomes into candidate phases and infer the order using continued fractions and modular checks.
6) Phase 6(Factor Extraction)- Use the estimated order to calculate nontrivial factors with GCD.
7) Phase 7(Validation and Reporting)- Compare the quantum estimate with the classical reference, save plots, and record experiment metrics.

## Virtual Environment Setup
Virtual Environment Commands- 
1) python -m venv .venv
2) .venv\Scripts\activate

After this install dependencies in venv using-
pip install -r requirements.txt 
## Running Phases 1-6

From the project directory, install dependencies and run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src/main.py
```

For a reproducible N=15, a=2 demonstration without input prompts:

```powershell
.\.venv\Scripts\python.exe src/main.py --defaults --shots 2048 --seed 42
```

The modular workflow prepares the work register in |1>, applies controlled
modular multiplication, inverse QFT, and measures the counting register in Aer.
Continued-fraction denominators from nonzero measurements are combined and
verified to estimate the order. GCD postprocessing then attempts factor extraction.
The classical Phase 2 reference is used only for comparison, never for inference.
Unsuccessful order recovery and unsuitable bases are reported explicitly.

The latest run writes these files to the project `results/` directory:
- `quantum_circuit.png`: Phase 3 circuit.
- `measurement_histogram.png`: Phase 4 measured counts.
- `experiment_results.csv`: one row per observed bitstring, inputs, classical
  reference, frequencies, estimated order, factors, and status.
- `run_log.txt`: parameters, library versions, timing, circuit details,
  measurements, and Phase 5/6 results.

These outputs cover the whole workflow, not just Phases 1 and 2. Each run
replaces the four files; use `--results-dir results/run_name` to retain separate runs.
CSV bitstrings should be imported as text in spreadsheet applications to retain
leading zeros. Counts and measured integers are also included.

This educational implementation uses dense permutation matrices and an ideal
statevector simulator: N <= 32 and 1-10 counting qubits. Work-register width is
computed from N; the legacy WORK_QUBITS setting is not used. The default eight
counting qubits suffice for N=15; use `--count-qubits 10` for larger examples.
The original `shor_demo.py` remains a separate legacy demonstration; use
`src/main.py` for the modular workflow and these output files.

## QuantumCrypt Web Frontend

A Streamlit application has been added. See `README_QUANTUMCRYPT.md` for setup and run `streamlit run app.py` after installing `requirements.txt`.
