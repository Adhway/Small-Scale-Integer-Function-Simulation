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