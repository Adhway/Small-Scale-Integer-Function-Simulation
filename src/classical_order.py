# Calculate modular powers and the reference order r

def find_classical_order(a, N):
    # Phase 2- Classical Order Finding
    print("\n" + "=" * 55)
    print(" PHASE 2: CLASSICAL ORDER FINDING")
    print("=" * 55)

    value = 1

    print(f"\nFinding the order of {a} modulo {N}:\n")

    # Check successive powers of a modulo N
    for r in range(1, N + 1):
        value = (value * a) % N

        print(f"{a}^{r} mod {N} = {value}")

        # The smallest positive r satisfying this is the order
        if value == 1:
            print(f"\nClassical order found: r = {r}")
            return r

    print("\nOrder not found within the search range.")
    return None


if __name__ == "__main__":
    # Standalone test using N = 15 and a = 2
    N = 15
    a = 2

    r = find_classical_order(a, N)

    if r is not None:
        print(f"Verification: {a}^{r} mod {N} = {pow(a, r, N)}")
