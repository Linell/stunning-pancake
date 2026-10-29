# Dog Breeds CLI

A small command-line program that prints a list of dog breeds.

## How to run it

You need Python 3. Open a terminal in this folder and type:

```
python dog_breeds.py
```

That prints every breed, one per line, in alphabetical order.

Some other things you can try:

```
python dog_breeds.py --search terrier   # only breeds with "terrier" in the name
python dog_breeds.py --count            # just print how many breeds there are
python dog_breeds.py --search spaniel --count   # how many spaniels?
python dog_breeds.py --help             # show all the options
```

Example output:

```
$ python dog_breeds.py --search terrier
Boston Terrier
Jack Russell Terrier
Yorkshire Terrier
```

## What I did and why (beginner notes)

**What is a "CLI"?** CLI stands for *command-line interface*. It's a program
you run by typing a command in the terminal instead of clicking buttons.
Extra words after the program name, like `--search terrier`, are called
*arguments* or *options*. They let the user change what the program does.

**Where do the breeds come from?** They're stored in a normal Python list
called `DOG_BREEDS` near the top of `dog_breeds.py`. I chose this instead of
downloading them from the internet so the program is simple and always
works, even offline. To add a breed, add another string to that list.

**How the code is organised.** The file has two functions:

- `find_breeds(search_text)` loops over the list and keeps the breeds whose
  name contains the search text. It turns both sides into lower case first
  with `.lower()`, so `Terrier`, `terrier` and `TERRIER` all match. Then it
  returns the matches sorted alphabetically. If the search text is empty,
  every name "contains" it, so you get the whole list.
- `main()` does the "talking to the user" part, in four steps:
  1. Describe which options the program accepts.
  2. Read what the user typed.
  3. Call `find_breeds` to get the matching breeds.
  4. Print them (or print the count, or a "no breeds found" message).

Keeping the searching separate from the printing is a good habit: each
function does one job, which makes them easier to read and to test.

**What is `argparse`?** It's a module that comes with Python. You tell it
which options your program has (`--search`, `--count`), and it reads them
from what the user typed. As a bonus, it builds the `--help` message for you
automatically and shows a friendly error if someone types an option that
doesn't exist.

**What does `if __name__ == "__main__":` do?** When you run a file directly,
Python sets a special variable `__name__` to `"__main__"`. That line means
"only call `main()` if this file was run directly". If another Python file
does `import dog_breeds` (for example to use `find_breeds`), the program
won't start printing things on its own.

## Ideas to try next

- Add more breeds to the list.
- Add a `--letter B` option that only shows breeds starting with a letter.
- Number each line of output (hint: look up `enumerate`).
