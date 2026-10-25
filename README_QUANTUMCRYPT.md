# QuantumCrypt — RSA Security Simulator Using Shor's Algorithm and QFT

A Streamlit front end for the existing small-scale Shor order-finding project. The app demonstrates a toy RSA workflow: encrypt readable UTF-8 text or numeric blocks, run the project's Qiskit/Aer Shor simulation, recover factors using order finding and GCD post-processing, derive the private exponent, and decrypt the message. The results include a block-by-block trace of the RSA decryption equation.

## Requirements

- Python 3.10–3.12 recommended
- A machine able to run Qiskit Aer statevector simulation

## Setup (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Setup (macOS / Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Streamlit prints a local URL, normally `http://localhost:8501`.

## First demo

- Choose modulus `N = 15`.
- Choose base `a = 2`.
- Use 1,024 or 2,048 shots and 8 counting qubits.
- Keep public exponent `e = 3`.
- Leave **Text message** selected and enter a phrase such as `HELLO QUANTUM`. Text is encoded into fixed-width base-N digits, each smaller than N.
- Alternatively, choose **Numeric blocks** and enter values such as `7, 4, 2`.
- Click **Run quantum factorization**. If the factors are recovered, expand **Step-by-step: how RSA decryption happened** to inspect every modular-exponentiation block and the text reconstruction.

For N=15, the intended factorization is 3 × 5 and φ(N)=8. Since e=3 is coprime to 8, the private exponent is d=3. Measurement-based order recovery can fail on a particular run; change the base, increase shots or adjust counting qubits and retry.

## Outputs

Each run saves the same artifacts as the core simulator into `results/web_runs/<run-settings>/`:

- `quantum_circuit.png`
- `measurement_histogram.png`
- `experiment_results.csv`
- `run_log.txt`

The UI also offers downloads for these files.

## Technical notes and limitations

- The backend is the project's existing Qiskit/Aer ideal simulation on a classical computer, not quantum hardware; it does not demonstrate quantum speedup.
- The dense permutation-unitary implementation is designed for small numbers (N ≤ 32 and no more than 5 work qubits). Do not use N above 32.
- The RSA exercise uses textbook RSA and numeric blocks only because the toy modulus cannot securely encode normal text. It is educational only and is not production cryptography.
- The classical reference order is reported only as a validation baseline; order inference comes from measurement outcomes and continued-fraction processing.
