"""Run the existing input/baseline stages followed by Phases 3 and 4."""
import argparse

if __package__:
    from . import config
    from .input_validate import get_inputs
    from .classical_order import find_classical_order
    from .quantum_circuit import build_quantum_circuit
    from .simulation import DEFAULT_RESULTS, run_simulation
else:
    import config
    from input_validate import get_inputs
    from classical_order import find_classical_order
    from quantum_circuit import build_quantum_circuit
    from simulation import DEFAULT_RESULTS, run_simulation


def main():
    parser = argparse.ArgumentParser(description="Shor simulation: Phases 1-6")
    parser.add_argument("--defaults", action="store_true", help="Use N and a from config.py")
    parser.add_argument("--shots", type=int, default=config.SHOTS)
    parser.add_argument("--count-qubits", type=int, default=config.COUNT_QUBITS)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--results-dir", default=DEFAULT_RESULTS)
    args = parser.parse_args()
    try:
        N, a = (config.N, config.a) if args.defaults else get_inputs()
        circuit = build_quantum_circuit(N, a, args.count_qubits)
        reference = find_classical_order(a, N)
        print("\nPHASE 3: QUANTUM CIRCUIT DESIGN")
        print(f"Circuit prepared with {circuit.num_qubits} qubits.")
        print("\nPHASE 4: FUNCTIONAL SIMULATION")
        counts = run_simulation(circuit, N, a, reference, args.shots, args.seed, args.results_dir)
        for bits, frequency in counts.items():
            print(f"{bits}: {frequency}")
        print(f"Results saved to: {args.results_dir}")
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
