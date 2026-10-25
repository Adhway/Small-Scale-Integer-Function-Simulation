# Phase 3: exact small-integer modular arithmetic and inverse QFT.
from math import gcd

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.circuit.library import QFTGate, UnitaryGate


def modular_multiplication_unitary(multiplier, modulus, work_qubits):
    """Map |x> to |multiplier*x mod N>; fix unused states x >= N.

    Dense permutation matrices are intended only for small-scale simulation.
    Coprimality makes the mapping bijective, hence unitary.
    """
    if modulus <= 2 or work_qubits < (modulus - 1).bit_length():
        raise ValueError("The work register must be large enough to represent N - 1.")
    if gcd(multiplier, modulus) != 1:
        raise ValueError("The multiplier and modulus must be coprime.")
    if work_qubits > 5:
        raise ValueError("This dense-matrix demonstration supports at most 5 work qubits.")
    dimension = 1 << work_qubits
    matrix = np.zeros((dimension, dimension), dtype=complex)
    for x in range(dimension):
        y = multiplier * x % modulus if x < modulus else x
        matrix[y, x] = 1
    return UnitaryGate(matrix, label=f"x{multiplier} mod {modulus}")


def build_quantum_circuit(N, a, count_qubits=8):
    """Build order-finding without using the classical reference order."""
    if N <= 2 or not 1 < a < N or gcd(a, N) != 1:
        raise ValueError("Use N > 2, 1 < a < N, and gcd(a, N) = 1.")
    work_qubits = (N - 1).bit_length()
    if work_qubits > 5 or not 1 <= count_qubits <= 10:
        raise ValueError("Use N <= 32 and 1 to 10 counting qubits for this demonstration.")
    count = QuantumRegister(count_qubits, "count")
    work = QuantumRegister(work_qubits, "work")
    bits = ClassicalRegister(count_qubits, "c")
    circuit = QuantumCircuit(count, work, bits)
    circuit.x(work[0])  # Little-endian work register starts in |1>.
    circuit.h(count)
    circuit.barrier()
    for j in range(count_qubits):
        multiplier = pow(a, 1 << j, N)
        # Multiplication by 1 is identity and needs no physical gate.
        if multiplier != 1:
            gate = modular_multiplication_unitary(multiplier, N, work_qubits)
            circuit.append(gate.control(1), [count[j], *work])
    circuit.barrier()
    circuit.append(QFTGate(count_qubits).inverse(), list(count))
    circuit.measure(count, bits)
    return circuit