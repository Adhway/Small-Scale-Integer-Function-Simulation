# Read N and a, validate inputs, check (gcd(a,N)=1).

from math import gcd


def get_inputs():
    # Phase 1- Input Setup and Validation
    print("=" * 55)
    print(" SHOR'S ORDER-FINDING ALGORITHM")
    print(" Phase 1: Input Setup and Validation")
    print("=" * 55)

    # Get the composite integer N
    try:
        N = int(input("Enter the composite integer N "))
    except ValueError:
        raise ValueError("N must be a valid integer.")

    # Validate N
    if N <= 2:
        raise ValueError("N must be greater than 2.")

    # Get the base a
    try:
        a = int(input("Enter the base a"))
    except ValueError:
        raise ValueError("a must be a valid integer.")

    # Validate the base range
    if not 1 < a < N:
        raise ValueError("The base must satisfy 1 < a < N.")

    # Check whether a and N are coprime
    common_divisor = gcd(a, N)

    if common_divisor != 1:
        print(f"\nGCD({a}, {N}) = {common_divisor}")

        if 1 < common_divisor < N:
            print("A non-trivial factor of N has already been found!")
            print(f"Factor: {common_divisor}")
            print(f"Other factor: {N // common_divisor}")

        raise ValueError(
            "The selected base and N are not coprime. "
            "Choose another base."
        )

    print("\nInput validation successful!")
    print(f"Input integer N : {N}")
    print(f"Base a          : {a}")
    print(f"GCD(a, N)       : {common_divisor}")

    return N, a


if __name__ == "__main__":
    N, a = get_inputs()
    print("\nPhase 1 completed successfully.")
