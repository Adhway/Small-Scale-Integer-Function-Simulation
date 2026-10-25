"""QuantumCrypt: educational RSA cryptanalysis using the project's Shor/QFT simulation."""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from src.classical_order import find_classical_order
from src.factorize import extract_factors
from src.order_estimate import estimate_order
from src.quantum_circuit import build_quantum_circuit
from src.simulation import run_simulation
from src.text_codec import decode_blocks_to_bytes, encode_text, group_digits

RESULTS = ROOT / "results" / "web_runs"

st.set_page_config(page_title="QuantumCrypt | RSA Security Lab", page_icon="⚛️", layout="wide")

st.markdown("""
<style>
    .stApp { background: #0b1020; color: #e8edf8; }
    [data-testid="stSidebar"] { background: #11182b; }
    .hero { padding: 1.55rem 1.8rem; border-radius: 18px; background: linear-gradient(120deg,#17294b,#17203b 60%,#202047); border: 1px solid #34476b; margin-bottom: 1.1rem; }
    .hero h1 { margin: 0; color: #f5f8ff; font-size: 2.2rem; }
    .hero p { color: #b9c8e4; margin: .55rem 0 0 0; font-size: 1.03rem; }
    .eyebrow { text-transform: uppercase; letter-spacing: .18em; font-size: .72rem; color: #7ee3d1; font-weight: 700; }
    .metric-card { background: #131d32; border: 1px solid #293956; border-radius: 14px; padding: 1rem 1.15rem; min-height: 108px; }
    .metric-label { color: #9eb0cf; font-size: .82rem; }
    .metric-value { color: #f2f6ff; font-size: 1.7rem; font-weight: 700; padding-top: .2rem; }
    .note { color: #9eb0cf; font-size: .88rem; }
    div[data-testid="stMetric"] { background: #131d32; border: 1px solid #293956; padding: 12px 15px; border-radius: 12px; }
    .stButton>button[kind="primary"] { background: #5eead4; color: #09212a; border: 0; font-weight: 750; }
</style>
<div class="hero">
 <div class="eyebrow">Quantum computing · Cryptography · Learning lab</div>
 <h1>⚛️ QuantumCrypt</h1>
 <p>Explore how Shor’s order-finding algorithm and the inverse Quantum Fourier Transform can threaten toy RSA keys.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Lab controls")
    st.caption("The quantum simulator is intentionally limited to small demonstration numbers.")
    N = st.selectbox("RSA modulus N", [15, 21], index=0, help="Choose a small product of two distinct primes supported by the current simulator.")
    a_options = [x for x in range(2, N) if math.gcd(x, N) == 1]
    a = st.selectbox("Shor base a", a_options, index=a_options.index(2) if 2 in a_options else 0)
    shots = st.select_slider("Measurement shots", options=[256, 512, 1024, 2048], value=1024)
    count_qubits = st.slider("Counting qubits", min_value=4, max_value=10, value=8)
    seed = st.number_input("Reproducibility seed", min_value=0, max_value=999999, value=42, step=1)
    st.divider()
    st.markdown("**Workflow**")
    st.caption("1 · Configure toy RSA\n\n2 · Run Shor + inverse QFT\n\n3 · Recover factors\n\n4 · Derive the private exponent\n\n5 · Decrypt text or numeric blocks")

# The current RSA UI offers only supported semiprimes; the backend itself supports N <= 32.

# Select a valid RSA exponent for the given toy modulus, default e=7 then 3, 5...
# For non-semiprime examples, factors/phi are only accepted when exactly two prime factors exist.
def rsa_prime_factors(n: int):
    factors = []
    value = n
    divisor = 2
    while divisor * divisor <= value:
        while value % divisor == 0:
            factors.append(divisor)
            value //= divisor
        divisor += 1
    if value > 1:
        factors.append(value)
    return factors

prime_factors = rsa_prime_factors(N)
if len(prime_factors) == 2 and prime_factors[0] != prime_factors[1]:
    p0, q0 = prime_factors
    phi0 = (p0 - 1) * (q0 - 1)
    valid_es = [e for e in range(3, phi0) if math.gcd(e, phi0) == 1 and e < N]
else:
    valid_es = []

main_tabs = st.tabs(["RSA Attack Lab", "QFT & Measurements", "Experiment Notes"])
with main_tabs[0]:
    st.subheader("Toy RSA encryption and quantum factorization")
    st.markdown("Encrypt a readable text message or use numeric blocks. For text, UTF-8 bytes are converted into fixed-width base-N digits so each RSA plaintext block remains smaller than the tiny modulus.")
    top1, top2, top3 = st.columns(3)
    top1.metric("Public modulus N", N)
    top2.metric("Selected base a", a)
    top3.metric("Quantum shots", f"{shots:,}")
    st.divider()

    left, right = st.columns([1.03, 1])
    with left:
        st.markdown("### 01 · Public key setup")
        if valid_es:
            default_e = 3 if 3 in valid_es else valid_es[0]
            e = st.selectbox("Public exponent e", valid_es, index=valid_es.index(default_e))
            st.code(f"Public key: (e={e}, N={N})")
        else:
            e = None
            st.error("This modulus is not a supported two-distinct-prime toy RSA modulus. Pick N = 15 or 21 for this demo.")
        message_mode = st.radio("Message format", ["Text message", "Numeric blocks"], horizontal=True, key="message_mode")
        original_text = ""
        text_bytes = b""
        block_width = 1
        if message_mode == "Text message":
            original_text = st.text_area(
                "Plaintext message", value="HELLO QUANTUM", height=90,
                max_chars=120,
                help="Any Unicode text is accepted. UTF-8 bytes are represented as base-N digits so every RSA block is smaller than N.",
            )
            try:
                encoded_text = encode_text(original_text, N)
                blocks = encoded_text.blocks
                text_bytes = encoded_text.utf8_bytes
                block_width = encoded_text.digits_per_byte
                blocks_ok = bool(blocks)
                st.caption(f"UTF-8 bytes: {len(text_bytes)} · RSA digit blocks: {len(blocks)} · {block_width} base-{N} digits per byte")
                with st.expander("See how text becomes RSA blocks"):
                    st.write("UTF-8 byte values")
                    st.code(", ".join(map(str, text_bytes)) if text_bytes else "(empty message)")
                    st.write(f"Base-{N} plaintext digit blocks")
                    st.code(", ".join(map(str, blocks)) if blocks else "(empty message)")
            except (UnicodeEncodeError, ValueError) as exc:
                blocks, blocks_ok = [], False
                st.warning(f"Could not encode this text: {exc}")
        else:
            blocks_text = st.text_input("Plaintext numeric blocks", value="7, 4, 2", help=f"Comma-separated integers in [0, {N-1}]. Example: 7, 4, 2")
            try:
                blocks = [int(token.strip()) for token in blocks_text.split(",") if token.strip()]
                blocks_ok = bool(blocks) and all(0 <= item < N for item in blocks)
            except ValueError:
                blocks, blocks_ok = [], False
            if not blocks_ok:
                st.warning(f"Enter comma-separated integers from 0 to {N-1}.")
        if blocks_ok:
            encrypted = [pow(m, e, N) for m in blocks] if e else []
            st.markdown("**Encrypted ciphertext blocks**")
            st.code(", ".join(map(str, encrypted)) if encrypted else "Choose a supported modulus")
            st.caption("Toy RSA uses textbook modular exponentiation for clarity. Do not use it to protect real messages.")
    with right:
        st.markdown("### 02 · Run Shor’s algorithm")
        st.write("The backend builds a controlled modular-multiplication circuit, applies inverse QFT to the counting register, samples measurements, and uses continued fractions plus GCD post-processing.")
        st.info("This is an ideal classical simulation of a quantum circuit, not a run on quantum hardware.")
        run_clicked = st.button("▶ Run quantum factorization", type="primary", use_container_width=True, disabled=(not valid_es or not blocks_ok))

    if run_clicked:
        if math.gcd(a, N) != 1:
            st.error("The chosen base and modulus must be coprime.")
        else:
            try:
                with st.spinner("Building the circuit and simulating measurements…"):
                    circuit = build_quantum_circuit(N, a, count_qubits)
                    classical_order = find_classical_order(a, N)
                    run_dir = RESULTS / f"N{N}_a{a}_s{shots}_q{count_qubits}_seed{seed}"
                    run_simulation(circuit, N, a, classical_order, shots, int(seed), run_dir)
                    import csv
                    with (run_dir / "experiment_results.csv").open(newline="", encoding="utf-8") as handle:
                        rows = list(csv.DictReader(handle))
                    counts = {}
                    for row in rows:
                        counts[row["bitstring"]] = int(row["frequency"])
                    order, evidence = estimate_order(counts, a, N, count_qubits)
                    factors, factor_status = extract_factors(a, N, order)
                    # Only calculate RSA private key if Shor recovered the two distinct prime factors.
                    is_semiprime_result = len(factors) == 2 and factors[0] * factors[1] == N and all(len(rsa_prime_factors(f)) == 1 for f in factors)
                    if is_semiprime_result:
                        p, q = factors
                        phi = (p - 1) * (q - 1)
                        d = pow(e, -1, phi) if math.gcd(e, phi) == 1 else None
                    else:
                        p = q = phi = d = None
                st.session_state["quantumcrypt_last"] = {
                    "N": N, "a": a, "shots": shots, "count_qubits": count_qubits,
                    "classical_order": classical_order, "order": order, "factors": factors,
                    "factor_status": factor_status, "counts": counts, "evidence": evidence,
                    "run_dir": str(run_dir), "e": e, "blocks": blocks, "encrypted": encrypted,
                    "message_mode": message_mode, "original_text": original_text,
                    "text_bytes": list(text_bytes), "block_width": block_width,
                    "p": p, "q": q, "phi": phi, "d": d, "is_semiprime_result": is_semiprime_result,
                    "circuit_depth": circuit.depth(), "total_qubits": circuit.num_qubits,
                }
            except Exception as exc:
                st.error(f"Simulation failed: {exc}")
                st.caption("Confirm the dependencies are installed from requirements.txt. Dense-unitary simulation can be resource-intensive; try fewer counting qubits or shots.")

    result = st.session_state.get("quantumcrypt_last")
    if result and result["N"] == N and result["a"] == a and result.get("message_mode") == message_mode and result.get("blocks") == blocks and result.get("e") == e:
        st.divider()
        st.markdown("### 03 · Results")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Estimated order r", str(result["order"] if result["order"] else "Not recovered"))
        c2.metric("Recovered factors", " × ".join(map(str, result["factors"])) if result["factors"] else "Not found")
        c3.metric("Circuit depth", result["circuit_depth"])
        c4.metric("Qubits", result["total_qubits"])
        if result["is_semiprime_result"] and result["d"] is not None:
            st.success(f"Factors recovered: {result['N']} = {result['p']} × {result['q']}. The RSA private exponent can now be derived.")
            cA, cB, cC = st.columns(3)
            cA.metric("Euler totient φ(N)", result["phi"])
            cB.metric("Private exponent d", result["d"])
            cC.metric("Public exponent e", result["e"])
            decrypted = [pow(c, result["d"], result["N"]) for c in result["encrypted"]]
            st.markdown("**Decryption demonstration**")
            cA, cB = st.columns(2)
            cA.markdown("Encrypted ciphertext blocks")
            cA.code(", ".join(map(str, result["encrypted"])))
            cB.markdown("Recovered plaintext digit blocks")
            cB.code(", ".join(map(str, decrypted)))
            if result.get("message_mode") == "Text message":
                try:
                    recovered_bytes = decode_blocks_to_bytes(decrypted, result["N"], result["block_width"])
                    recovered_text = recovered_bytes.decode("utf-8")
                    st.markdown("#### Recovered text")
                    st.success(recovered_text if recovered_text else "(empty text message)")
                    st.caption("The recovered text matches the original input." if recovered_text == result["original_text"] else "The recovered text differs from the original; inspect the block trace below.")
                except (ValueError, UnicodeDecodeError) as exc:
                    recovered_bytes = b""
                    recovered_text = None
                    st.error(f"Text decoding failed after RSA decryption: {exc}")
            else:
                st.caption("The decrypted blocks should match the numeric plaintext blocks.")
            with st.expander("Step-by-step: how RSA decryption happened", expanded=True):
                st.markdown("**1. Recover the factors and compute the totient**")
                st.latex(r"N = p q = " + str(result["p"]) + r"\times" + str(result["q"]))
                st.latex(r"\varphi(N)=(p-1)(q-1)=" + str(result["phi"]))
                st.markdown("**2. Find the private exponent**")
                st.latex(r"d=e^{-1}\pmod{\varphi(N)}")
                st.latex(str(result["e"]) + r"\cdot" + str(result["d"]) + r"\equiv 1\pmod{" + str(result["phi"]) + "}")
                st.markdown("**3. Decrypt each ciphertext block**")
                st.latex(r"m_i=c_i^d\bmod N")
                import pandas as pd
                trace_rows = [{
                    "Block": i + 1,
                    "Ciphertext c": c,
                    "Calculation": f"{c}^{result['d']} mod {result['N']}",
                    "Recovered digit m": m,
                } for i, (c, m) in enumerate(zip(result["encrypted"], decrypted))]
                st.dataframe(pd.DataFrame(trace_rows), use_container_width=True, hide_index=True)
                if result.get("message_mode") == "Text message" and recovered_text is not None:
                    st.markdown(f"**4. Rebuild UTF-8 bytes from groups of {result['block_width']} base-{result['N']} digits**")
                    st.write("Each group is converted back from base N to one byte, then the bytes are decoded as UTF-8 text.")
                    byte_rows = []
                    for byte_index, group in enumerate(group_digits(decrypted, result["block_width"])):
                        value = 0
                        for digit in group:
                            value = value * result["N"] + digit
                        byte_val = value
                        byte_rows.append({
                            "UTF-8 byte #": byte_index + 1,
                            "Decrypted base-N digits": ", ".join(map(str, group)),
                            "Reconstructed byte": byte_val,
                            "ASCII preview": chr(byte_val) if 32 <= byte_val <= 126 else "(UTF-8 byte)",
                        })
                    st.dataframe(pd.DataFrame(byte_rows), use_container_width=True, hide_index=True)
                    st.markdown("**5. Decode bytes into the original text**")
                    st.code(recovered_bytes.decode("utf-8"))
            st.caption("This is textbook RSA with tiny educational keys and a simple reversible text encoding. It is not secure padding or production cryptography.")
        else:
            st.warning(f"Factor extraction was unsuccessful for this run. {result['factor_status']} Try a different coprime base, more shots, or more counting qubits.")
        with st.expander("Show order-finding evidence"):
            st.write(f"Classical reference order (validation only): {result['classical_order']}")
            st.write("The classical reference is not supplied to the quantum circuit or the order-estimation routine.")
            if result["evidence"]:
                for line in result["evidence"]:
                    st.code(line)
            else:
                st.write("No measurement gave a sufficiently useful continued-fraction approximation in this run.")

with main_tabs[1]:
    st.subheader("Quantum Fourier Transform and measurement explorer")
    result = st.session_state.get("quantumcrypt_last")
    st.write("QFT changes the representation of phase information. In Shor’s order-finding circuit, the inverse QFT helps turn periodicity into measurement outcomes that can be analyzed with continued fractions.")
    if result:
        results_dir = Path(result["run_dir"])
        circuit_image = results_dir / "quantum_circuit.png"
        histogram_image = results_dir / "measurement_histogram.png"
        ic1, ic2 = st.columns(2)
        with ic1:
            st.markdown("**Circuit used in the last run**")
            if circuit_image.exists():
                st.image(str(circuit_image), use_container_width=True)
            else:
                st.caption("Circuit image is unavailable.")
        with ic2:
            st.markdown("**Measurement histogram**")
            if histogram_image.exists():
                st.image(str(histogram_image), use_container_width=True)
            else:
                st.caption("Histogram is unavailable.")
        st.markdown("**Observed measurement counts**")
        import pandas as pd
        df = pd.DataFrame([{"Bitstring": k, "Measured integer": int(k, 2), "Shots": v, "Probability": v / result["shots"]} for k, v in sorted(result["counts"].items(), key=lambda kv: -kv[1])])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Run the quantum factorization from the RSA Attack Lab tab to populate the circuit and measurement charts.")

with main_tabs[2]:
    st.subheader("How to interpret this demonstration")
    st.markdown("""
**What this project demonstrates**
- RSA’s toy modulus is factored using the project’s Shor order-finding simulation.
- The quantum circuit uses controlled modular multiplication followed by the inverse Quantum Fourier Transform.
- Measurement outcomes are post-processed with continued fractions and modular checks to estimate the order.
- Classical GCD post-processing derives factors, and the factors allow a toy RSA private exponent to be reconstructed.

**Important limitations**
- The backend uses an ideal Aer statevector simulator on a classical computer; this is not evidence of quantum speedup.
- Dense matrix operations limit supported inputs to small integers (N ≤ 32 in the current implementation).
- Real RSA keys are far beyond the capabilities of this demonstration.
- The app supports text and numeric blocks. Text is encoded as UTF-8 bytes and fixed-width base-N digits before textbook RSA encryption; this is a teaching codec, not secure padding or production cryptography.
""")
    result = st.session_state.get("quantumcrypt_last")
    if result:
        folder = Path(result["run_dir"])
        st.markdown("**Artifacts from the last run**")
        for filename in ["quantum_circuit.png", "measurement_histogram.png", "experiment_results.csv", "run_log.txt"]:
            file_path = folder / filename
            if file_path.exists():
                st.download_button(f"Download {filename}", data=file_path.read_bytes(), file_name=filename, key=f"download_{filename}")

st.markdown("---")
st.markdown('<p class="note">QuantumCrypt · Educational prototype · Do not use toy RSA for real secrets.</p>', unsafe_allow_html=True)