
from math import gcd
from fractions import Fraction

import matplotlib.pyplot as plt
from qiskit import (
    QuantumCircuit,
    QuantumRegister,
    ClassicalRegister,
    transpile
)

from qiskit.circuit.library import UnitaryGate, QFTGate
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram

# ==========================================
# PARAMETERS
# ==========================================
N = 15
a = 2
SHOTS = 2048
COUNT_QUBITS = 8
WORK_QUBITS = 4


# ==========================================
# PHASE 1: VALIDATE INPUTS
# ==========================================
print("=" * 50)
print("SHOR'S ORDER-FINDING: N = 15, a = 2")
print("=" * 50)

if N <= 2 or not (1 < a < N):
    raise ValueError("Use N > 2 and 1 < a < N.")

if gcd(a, N) != 1:
    print("A non-trivial factor is already available:", gcd(a, N))
    raise SystemExit


# ==========================================
# PHASE 2: CLASSICAL BASELINE
# ==========================================
print("\nPHASE 2: CLASSICAL BASELINE")

value = 1
classical_order = None

for r in range(1, N + 1):
    value = (value * a) % N
    print(f"{a}^{r} mod {N} = {value}")

    if value == 1:
        classical_order = r
        break

print("Expected classical order:", classical_order)


# ==========================================
# MODULAR MULTIPLICATION UNITARY
# ==========================================
def modular_multiplication_unitary(multiplier, modulus):
    """Create a permutation unitary for small-modulus arithmetic."""
    dimension = 2 ** WORK_QUBITS
    matrix = [[0] * dimension for _ in range(dimension)]

    for x in range(dimension):
        if 1 <= x < modulus:
            y = (multiplier * x) % modulus
        else:
            # Keep zero and unused basis states unchanged.
            y = x

        matrix[y][x] = 1

    return UnitaryGate(matrix, label=f"Mul mod {modulus}")


# ==========================================
# PHASE 3: BUILD QUANTUM CIRCUIT
# ==========================================
print("\nPHASE 3: BUILDING QUANTUM CIRCUIT")

count = QuantumRegister(COUNT_QUBITS, "count")
work = QuantumRegister(WORK_QUBITS, "work")
c = ClassicalRegister(COUNT_QUBITS, "c")

qc = QuantumCircuit(count, work, c)

# Initialize the work register to |1>
qc.x(work[0])

# Create an equal superposition in the counting register
qc.h(count)

# Controlled modular exponentiation:
# U^(2^j) implements multiplication by a^(2^j) mod N.
for j in range(COUNT_QUBITS):
    multiplier = pow(a, 2**j, N)

    U = modular_multiplication_unitary(multiplier, N)
    controlled_U = U.control(1)

    qc.append(controlled_U, [count[j], *work])

# Inverse Quantum Fourier Transform
qc.append(QFTGate(COUNT_QUBITS).inverse(), list(count))

# Measure the counting register
qc.measure(count, c)

print("Counting qubits:", COUNT_QUBITS)
print("Work qubits:", WORK_QUBITS)
print("Total qubits:", qc.num_qubits)
print("\nCircuit:")
print(qc.draw(output="text", fold=100))



# ==========================================
# PHASE 4: SIMULATION
# ==========================================
print("\nPHASE 4: RUNNING QUANTUM SIMULATION")

simulator = AerSimulator()

# Decompose unsupported composite instructions,
# such as controlled generic unitary operations,
# into gates supported by the simulator.
print("Transpiling quantum circuit for Aer...")

compiled_qc = transpile(
    qc,
    backend=simulator,
    optimization_level=1
)

print("Circuit transpilation completed.")
print("Compiled circuit depth:", compiled_qc.depth())
print("Compiled circuit gate counts:", compiled_qc.count_ops())

# Execute the transpiled circuit
job = simulator.run(
    compiled_qc,
    shots=SHOTS
)

result = job.result()
counts = result.get_counts()

print("\nMeasurement counts:")

for bitstring, frequency in sorted(
    counts.items(),
    key=lambda item: item[1],
    reverse=True
):
    print(f"{bitstring}: {frequency}")

# ==========================================
# PHASE 5: ESTIMATE ORDER FROM MEASUREMENTS
# ==========================================
print("\nPHASE 5: ESTIMATING THE ORDER")

estimated_order = None
modulus_size = 2**COUNT_QUBITS

# Examine frequently observed phases first.
for bitstring, frequency in sorted(
    counts.items(), key=lambda item: item[1], reverse=True
):
    measured_value = int(bitstring.replace(" ", ""), 2)
    phase = Fraction(measured_value, modulus_size)
    candidate = phase.limit_denominator(N).denominator

    print(
        f"Measurement={bitstring}, "
        f"frequency={frequency}, "
        f"phase={phase}, candidate denominator={candidate}"
    )

    # A denominator may be a divisor of the true order.
    # Test its multiples against modular arithmetic.
    for multiple in range(1, N // candidate + 1):
        r = candidate * multiple

        if pow(a, r, N) == 1:
            estimated_order = r
            break

    if estimated_order is not None:
        break

if estimated_order is None:
    print("No valid order recovered. More trials or analysis are needed.")
    raise SystemExit

print("Estimated order:", estimated_order)


# ==========================================
# PHASE 6: CLASSICAL FACTOR EXTRACTION
# ==========================================
print("\nPHASE 6: FACTOR EXTRACTION")

if estimated_order % 2 != 0:
    print("The estimated order is odd; try another measurement or base.")
    raise SystemExit

half_power = pow(a, estimated_order // 2, N)

if half_power == N - 1:
    print("The order gives -1 modulo N; try another base.")
    raise SystemExit

factor1 = gcd(half_power - 1, N)
factor2 = gcd(half_power + 1, N)

factors = sorted({
    factor for factor in (factor1, factor2)
    if 1 < factor < N
})

print("a^(r/2) mod N:", half_power)
print("Candidate factors:", factors)


# ==========================================
# PHASE 7: VALIDATION AND VISUALIZATION
# ==========================================
print("\nPHASE 7: VALIDATION")

print("N:", N)
print("a:", a)
print("Classical order:", classical_order)
print("Quantum-estimated order:", estimated_order)
print("Order matches baseline:", estimated_order == classical_order)
print("Factorization:", factors)

if len(factors) == 2:
    print("Factor product:", factors[0] * factors[1])
    print("Factorization valid:", factors[0] * factors[1] == N)

plot_histogram(counts)
plt.title("Quantum Order-Finding: N=15, a=2")
plt.tight_layout()
plt.savefig("results/demo_histogram.png", dpi=150)
plt.show()

print("\nHistogram saved as measurement_histogram.png")
