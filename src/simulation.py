# Phase 4: execute in Aer and save raw measurements and run artifacts.
import csv
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from qiskit import transpile
import qiskit
import qiskit_aer
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram

DEFAULT_RESULTS = Path(__file__).resolve().parents[1] / "results"

if __package__:
    from .order_estimate import estimate_order
    from .factorize import extract_factors
else:
    from order_estimate import estimate_order
    from factorize import extract_factors


def run_simulation(circuit, N, a, classical_order, shots=2048, seed=42,
                   results_dir=DEFAULT_RESULTS):
    # Save the latest execution, including Phases 5 and 6 postprocessing.
    if shots <= 0:
        raise ValueError("Shots must be a positive integer.")
    output = Path(results_dir)
    output.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    start = perf_counter()
    simulator = AerSimulator(method="statevector")
    compiled = transpile(circuit, simulator, optimization_level=1, seed_transpiler=seed)
    transpile_seconds = perf_counter() - start
    start = perf_counter()
    result = simulator.run(compiled, shots=shots, seed_simulator=seed).result()
    if not result.success:
        raise RuntimeError(f"Aer simulation failed: {result.status}")
    counts = dict(sorted(result.get_counts().items()))
    simulation_seconds = perf_counter() - start
    if sum(counts.values()) != shots:
        raise RuntimeError("Measurement counts do not add up to the requested shots.")
    estimated_order, evidence = estimate_order(counts, a, N, circuit.num_clbits)
    factors, factor_status = extract_factors(a, N, estimated_order)
    print(f"\nPHASE 5: Estimated order = {estimated_order}")
    print(f"PHASE 6: Factors = {factors}. {factor_status}")

    figure = circuit.draw(output="mpl", fold=40)
    figure.savefig(output / "quantum_circuit.png", dpi=150, bbox_inches="tight")
    plt.close(figure)
    figure = plot_histogram(counts, title=f"Phase 4 measurements: N={N}, a={a}, shots={shots}")
    figure.savefig(output / "measurement_histogram.png", dpi=150, bbox_inches="tight")
    plt.close(figure)

    with (output / "experiment_results.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["run_utc", "N", "a", "classical_reference_order", "count_qubits",
                         "work_qubits", "shots", "seed", "bitstring", "measured_integer",
                         "frequency", "empirical_probability", "estimated_order", "factors",
                         "order_matches_baseline", "factor_status"])
        for bits, frequency in counts.items():
            writer.writerow([started, N, a, classical_order, circuit.num_clbits,
                             circuit.num_qubits - circuit.num_clbits, shots, seed,
                             bits, int(bits, 2), frequency, frequency / shots, estimated_order,
                             ";".join(map(str, factors)), estimated_order == classical_order, factor_status])

    lines = ["Shor order-finding: Phases 1-6", f"Run UTC: {started}",
             f"N={N}, a={a}", f"Classical reference order: {classical_order}",
             "The reference order is recorded only; it is not used to build the circuit.",
             f"Qiskit: {qiskit.__version__}; Aer: {qiskit_aer.__version__}",
             f"Backend: AerSimulator (ideal statevector); shots={shots}; seed={seed}",
             f"Counting qubits: {circuit.num_clbits}; total qubits: {circuit.num_qubits}",
             f"Logical depth: {circuit.depth()}; compiled depth: {compiled.depth()}",
             f"Compiled operations: {dict(compiled.count_ops())}",
             f"Transpilation seconds: {transpile_seconds:.6f}",
             f"Simulation seconds: {simulation_seconds:.6f}",
             "Bitstrings are displayed most-significant bit first (c[n-1] ... c[0]).",
             "Measurement counts:", *[f"  {bits}: {n}" for bits, n in counts.items()],
             "Phase 5 evidence:", *evidence, f"Estimated order: {estimated_order}",
             f"Order matches classical baseline: {estimated_order == classical_order}",
             f"Phase 6 factors: {factors}", factor_status,
             "", str(circuit.draw(output="text", fold=100))]
    (output / "run_log.txt").write_text("\n".join(lines), encoding="utf-8")
    return counts
