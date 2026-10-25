# Phase 5: recover an order from continued-fraction measurement candidates.
from fractions import Fraction
from math import lcm


def estimate_order(counts, a, N, count_qubits):
    # Combine measured denominators; never search from the zero outcome.
    candidates = {1}
    evidence = []
    scale = 1 << count_qubits
    for bits, frequency in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        measured = int(bits, 2)
        if measured == 0 or frequency <= 0:
            continue
        phase = Fraction(measured, scale)
        approximation = phase.limit_denominator(N - 1)
        denominator = approximation.denominator
        # Reject rationals that are not within half a measurement bin.
        if denominator == 1 or abs(phase - approximation) > Fraction(1, 2 * scale):
            continue
        evidence.append(f"{bits}: {frequency} shots, phase={phase}, approximation={approximation}")
        candidates |= {lcm(previous, denominator) for previous in tuple(candidates)
                       if lcm(previous, denominator) < N}
        for candidate in sorted(candidates - {1}):
            if pow(a, candidate, N) == 1:
                # Reduce a verified multiple to its smallest order.
                order = candidate
                for divisor in range(2, candidate + 1):
                    while order % divisor == 0 and pow(a, order // divisor, N) == 1:
                        order //= divisor
                return order, evidence
    return None, evidence
