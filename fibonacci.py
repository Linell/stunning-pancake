# fibonacci.py
#
# Prints the Fibonacci sequence, using a *recursive* function to work out
# each number. (A recursive function is one that calls itself.)
#
# The Fibonacci sequence starts 0, 1, and then every number is the sum of
# the two numbers before it:
#
#     0, 1, 1, 2, 3, 5, 8, 13, 21, 34, ...
#
# How to run it (from the folder this file is in):
#
#     python fibonacci.py          # print the first 10 Fibonacci numbers
#     python fibonacci.py 15       # print the first 15 Fibonacci numbers
#     python fibonacci.py --help   # show the options

# "argparse" is part of Python's standard library (nothing to install).
# It reads what the user typed after the program name, like the 15 above.
import argparse


def fibonacci(n):
    """Return the n-th Fibonacci number, counting from 0.

    fibonacci(0) is 0, fibonacci(1) is 1, fibonacci(2) is 1,
    fibonacci(3) is 2, and so on.
    """
    # --- The "base cases": answers we know without any work. ---
    # Every recursive function needs at least one of these, otherwise it
    # would keep calling itself forever.
    if n == 0:
        return 0
    if n == 1:
        return 1

    # --- The "recursive case": the function calls itself. ---
    # The n-th number is the sum of the two numbers before it.
    # Each call uses a smaller n, so we always end up at a base case.
    return fibonacci(n - 1) + fibonacci(n - 2)


def main():
    """Read the command-line options and print the sequence."""

    # --- Step 1: describe the options our program accepts. ---
    parser = argparse.ArgumentParser(
        description="Print the Fibonacci sequence (computed with recursion)."
    )
    parser.add_argument(
        "how_many",
        type=int,      # argparse turns the text "15" into the number 15
        nargs="?",     # "?" means this argument is optional...
        default=10,    # ...and if it's left out, we use 10
        help="how many Fibonacci numbers to print (default: 10)",
    )

    # --- Step 2: read what the user actually typed. ---
    args = parser.parse_args()

    # --- Step 3: check the number makes sense. ---
    # You can't print a negative amount of numbers.
    # parser.error() prints a friendly message and stops the program.
    if args.how_many < 0:
        parser.error("how_many must be 0 or more")

    # --- Step 4: print each Fibonacci number, one per line. ---
    # range(args.how_many) gives 0, 1, 2, ... up to (but not including)
    # how_many, so we print exactly how_many numbers.
    for position in range(args.how_many):
        print(fibonacci(position))


# This line means "only run main() when this file is run directly",
# not when another Python file imports it.
if __name__ == "__main__":
    main()
