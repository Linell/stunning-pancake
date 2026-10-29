# dog_breeds.py
#
# A small command-line program (a "CLI") that lists breeds of dog.
#
# How to run it (from the folder this file is in):
#
#     python dog_breeds.py                 # list every breed
#     python dog_breeds.py --search terrier  # only breeds containing "terrier"
#     python dog_breeds.py --count         # just show how many breeds there are
#
# You can also ask the program for help:
#
#     python dog_breeds.py --help

# "argparse" is part of Python's standard library (nothing to install).
# It reads the options the user typed after the program name, like --search.
import argparse


# ---------------------------------------------------------------------------
# The data: a plain Python list of breed names.
# Keeping it in the file means the program works without internet access.
# To add a breed, just add another string to this list.
# ---------------------------------------------------------------------------
DOG_BREEDS = [
    "Australian Shepherd",
    "Basset Hound",
    "Beagle",
    "Bernese Mountain Dog",
    "Bichon Frise",
    "Border Collie",
    "Boston Terrier",
    "Boxer",
    "Bulldog",
    "Cavalier King Charles Spaniel",
    "Chihuahua",
    "Cocker Spaniel",
    "Dachshund",
    "Dalmatian",
    "Doberman Pinscher",
    "French Bulldog",
    "German Shepherd",
    "Golden Retriever",
    "Great Dane",
    "Greyhound",
    "Husky",
    "Jack Russell Terrier",
    "Labrador Retriever",
    "Maltese",
    "Pomeranian",
    "Poodle",
    "Pug",
    "Rottweiler",
    "Saint Bernard",
    "Shih Tzu",
    "Whippet",
    "Yorkshire Terrier",
]


def find_breeds(search_text):
    """Return a sorted list of breeds whose name contains search_text.

    The match ignores upper/lower case, so "TERRIER" and "terrier" both work.
    If search_text is empty, every breed is returned.
    """
    # Lower-case the search text once so we can compare fairly.
    search_text = search_text.lower()

    # Build up a new list containing only the breeds that match.
    matches = []
    for breed in DOG_BREEDS:
        if search_text in breed.lower():
            matches.append(breed)

    # sorted() gives back a new list in alphabetical order.
    return sorted(matches)


def main():
    """Read the command-line options and print the results."""

    # --- Step 1: describe the options our program accepts. ---
    parser = argparse.ArgumentParser(description="List breeds of dog.")
    parser.add_argument(
        "--search",
        default="",
        help="only show breeds whose name contains this text",
    )
    parser.add_argument(
        "--count",
        action="store_true",  # means: True if the flag is given, else False
        help="only print how many breeds match",
    )

    # --- Step 2: read what the user actually typed. ---
    args = parser.parse_args()

    # --- Step 3: find the matching breeds. ---
    breeds = find_breeds(args.search)

    # --- Step 4: print the results. ---
    if args.count:
        print(len(breeds))
    elif len(breeds) == 0:
        print("No breeds found matching '" + args.search + "'.")
    else:
        for breed in breeds:
            print(breed)


# This line means "only run main() when this file is run directly",
# not when another Python file imports it.
if __name__ == "__main__":
    main()
