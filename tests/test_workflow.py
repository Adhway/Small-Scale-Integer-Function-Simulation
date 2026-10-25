"""Numerical checks for the small-scale quantum workflow."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import numpy as np
from qiskit.quantum_info import Statevector
from quantum_circuit import build_quantum_circuit, modular_multiplication_unitary
from order_estimate import estimate_order
from factorize import extract_factors


class WorkflowTests(unittest.TestCase):
    def test_modular_mapping_and_unitarity(self):
        for N, a in [(15, 2), (21, 2)]:
            width = (N - 1).bit_length()
            matrix = np.asarray(modular_multiplication_unitary(a, N, width))
            np.testing.assert_allclose(matrix.conj().T @ matrix, np.eye(1 << width))
            for x in range(1 << width):
                self.assertEqual(np.argmax(abs(matrix[:, x])), a * x % N if x < N else x)

    def test_quantum_peaks(self):
        circuit = build_quantum_circuit(15, 2, 8).remove_final_measurements(inplace=False)
        probabilities = Statevector.from_instruction(circuit).probabilities(qargs=list(range(8)))
        expected = np.zeros(256)
        expected[[0, 64, 128, 192]] = 0.25
        np.testing.assert_allclose(probabilities, expected, atol=1e-10)

    def test_order_estimation(self):
        self.assertEqual(estimate_order({"01000000": 100}, 2, 15, 8)[0], 4)
        self.assertIsNone(estimate_order({"00000000": 100}, 2, 15, 8)[0])
        self.assertIsNone(estimate_order({"10000000": 100}, 2, 15, 8)[0])
        # Combine denominators 2 and 3 to recover order 6, without a reference.
        self.assertEqual(estimate_order({"10000000": 100, "01010101": 90}, 2, 21, 8)[0], 6)

    def test_factor_extraction(self):
        self.assertEqual(extract_factors(2, 15, 4)[0], [3, 5])
        self.assertEqual(extract_factors(2, 21, 6)[0], [3, 7])
        self.assertEqual(extract_factors(4, 21, 3)[0], [])
        self.assertEqual(extract_factors(14, 15, 2)[0], [])
        self.assertEqual(extract_factors(2, 15, None)[0], [])


if __name__ == "__main__":
    unittest.main()
