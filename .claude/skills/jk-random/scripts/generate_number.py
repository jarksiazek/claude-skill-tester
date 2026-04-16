#!/usr/bin/env python3
"""Generate a random number with customizable bounds."""

import random
import sys

def generate_random_number(min_val=1, max_val=100):
    """Generate a random integer between min_val and max_val (inclusive)."""
    return random.randint(min_val, max_val)

if __name__ == "__main__":
    min_val = 1
    max_val = 100

    # Parse command-line arguments
    if len(sys.argv) >= 2:
        try:
            min_val = int(sys.argv[1])
        except ValueError:
            print(f"Error: Lower bound must be an integer, got '{sys.argv[1]}'")
            sys.exit(1)

    if len(sys.argv) >= 3:
        try:
            max_val = int(sys.argv[2])
        except ValueError:
            print(f"Error: Upper bound must be an integer, got '{sys.argv[2]}'")
            sys.exit(1)

    # Validate bounds
    if min_val > max_val:
        print(f"Error: Lower bound ({min_val}) cannot be greater than upper bound ({max_val})")
        sys.exit(1)

    number = generate_random_number(min_val, max_val)
    print(f"🎲 Your random number is: {number}")
