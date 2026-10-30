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

---

# Fibonacci Sequence (with recursion)

`fibonacci.py` prints the Fibonacci sequence. It works out each number with
a *recursive* function.

## How to run it

Open a terminal in this folder and type:

```
python fibonacci.py          # print the first 10 Fibonacci numbers
python fibonacci.py 15       # print the first 15
python fibonacci.py --help   # show the options
```

Example output:

```
$ python fibonacci.py 8
0
1
1
2
3
5
8
13
```

## What I did and why (beginner notes)

**Python or Go?** You could do this in either language. I picked Python
because you already know it, so you can focus on the new idea (recursion)
instead of learning a new language too.

**What is the Fibonacci sequence?** It starts with 0 and 1. After that, each
number is the two numbers before it added together:
0, 1, 1 (0+1), 2 (1+1), 3 (1+2), 5 (2+3), 8 (3+5), and so on.

**What is recursion?** Recursion is when a function calls *itself*. It's
handy when a problem can be split into smaller versions of the same
problem. Fibonacci is the classic example, because the rule is already
written in terms of itself: "the n-th number = the (n-1)-th number + the
(n-2)-th number".

A recursive function always has two parts:

1. **Base cases**: small inputs where we know the answer straight away.
   Here, `fibonacci(0)` is `0` and `fibonacci(1)` is `1`. Without these,
   the function would call itself forever (Python would stop it with a
   `RecursionError`).
2. **The recursive case**: for anything bigger, return
   `fibonacci(n - 1) + fibonacci(n - 2)`. Each call uses a smaller `n`, so
   we always work our way down to a base case.

Here's what happens when you ask for `fibonacci(4)`:

```
fibonacci(4)
= fibonacci(3) + fibonacci(2)
= (fibonacci(2) + fibonacci(1)) + (fibonacci(1) + fibonacci(0))
= ((fibonacci(1) + fibonacci(0)) + 1) + (1 + 0)
= ((1 + 0) + 1) + 1
= 3
```

**How the code is organised.** Like `dog_breeds.py`, the file has two
functions, one job each:

- `fibonacci(n)` does the maths and returns one number.
- `main()` reads what you typed, checks it isn't negative, then loops from
  0 up to the amount you asked for, printing `fibonacci(position)` each time.

The amount (`how_many`) is optional. In `add_argument`, `nargs="?"` means
"this can be left out" and `default=10` is used when it is. `type=int`
makes argparse turn the text you typed into a number, and it shows an error
if you type something that isn't a whole number, like `abc`.

**A warning: this gets slow.** Notice in the example above that
`fibonacci(2)` was worked out twice. For bigger numbers the same work is
repeated a *huge* number of times: each time `n` goes up by 1,
the number of calls grows by about 1.6 times. On my test, printing 30 numbers took
about 0.3 seconds, but 35 took nearly 3 seconds, and 45 would take minutes.
That's expected for this simple version. It's written this way to show
recursion clearly, not to be fast.

## Ideas to try next

- Add a `print` at the start of `fibonacci` to watch every call happen
  (try it with a small number like 5!).
- Count how many times `fibonacci` gets called for different numbers.
- Make it fast with *memoization*: store each answer in a dictionary the
  first time you work it out, and check the dictionary before doing the
  work again.
- Write a version that uses a `for` loop instead of recursion and compare
  how fast they are.
