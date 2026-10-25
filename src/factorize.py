# Phase 6: classical factor extraction from a verified even order.
from math import gcd


def extract_factors(a, N, order):
    if order is None:
        return [], "No order recovered; try more shots or counting qubits."
    if order <= 0 or pow(a, order, N) != 1:
        return [], "The supplied order failed modular verification."
    if order % 2:
        return [], "The order is odd; choose another coprime base."
    half_power = pow(a, order // 2, N)
    if half_power in (1, N - 1):
        return [], "The half-power gives only trivial factors; choose another base."
    factors = sorted({factor for factor in (gcd(half_power - 1, N), gcd(half_power + 1, N))
                      if 1 < factor < N})
    return factors, "Nontrivial factors recovered." if factors else "Only trivial factors recovered."
