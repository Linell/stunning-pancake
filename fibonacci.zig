// fibonacci.zig
//
// Prints the Fibonacci sequence, using a *recursive* function to work out
// each number. (A recursive function is one that calls itself.)
// This is the Zig version of fibonacci.py, and it works the same way.
//
// The Fibonacci sequence starts 0, 1, and then every number is the sum of
// the two numbers before it:
//
//     0, 1, 1, 2, 3, 5, 8, 13, 21, 34, ...
//
// How to run it (from the folder this file is in). Written for Zig 0.17.0:
//
//     zig run fibonacci.zig            # print the first 10 Fibonacci numbers
//     zig run fibonacci.zig -- 15      # print the first 15 Fibonacci numbers
//
// The "--" tells `zig run` that everything after it is for OUR program,
// not for the zig tool itself.

// "std" is Zig's standard library (like Python's built-in modules).
// @import is how Zig loads it. Nothing extra to install.
const std = @import("std");

// The biggest position we allow. fibonacci(93) is the largest Fibonacci
// number that fits in a u64 (an unsigned 64-bit whole number). Asking for
// 94 numbers means positions 0 to 93, so 94 is the most we can print.
// (In practice the slow recursion means you won't want to go near this!)
const max_how_many: u64 = 94;

/// Return the n-th Fibonacci number, counting from 0.
///
/// fibonacci(0) is 0, fibonacci(1) is 1, fibonacci(2) is 1,
/// fibonacci(3) is 2, and so on.
///
/// In Zig you must say the type of every parameter and of the return
/// value. "u64" means "unsigned 64-bit integer": a whole number that can't
/// be negative.
fn fibonacci(n: u64) u64 {
    // --- The "base cases": answers we know without any work. ---
    // Every recursive function needs at least one of these, otherwise it
    // would keep calling itself forever.
    if (n == 0) {
        return 0;
    }
    if (n == 1) {
        return 1;
    }

    // --- The "recursive case": the function calls itself. ---
    // The n-th number is the sum of the two numbers before it.
    // Each call uses a smaller n, so we always end up at a base case.
    return fibonacci(n - 1) + fibonacci(n - 2);
}

/// main is where the program starts, just like main() in the Python file.
///
/// "init" is handed to us by Zig. It gives us the command-line arguments,
/// a memory allocator, and "io" (what we need to print things).
///
/// The "!" in "!void" means "this function returns nothing, but it might
/// fail with an error". The "try" keyword below says "if this fails, stop
/// and pass the error up".
pub fn main(init: std.process.Init) !void {
    // --- Step 1: set up a way to print to the terminal (stdout). ---
    // Zig collects our output in a buffer (a block of memory) and sends it
    // out in chunks, which is faster than sending one character at a time.
    var stdout_buffer: [1024]u8 = undefined;
    var stdout_file_writer: std.Io.File.Writer = .init(.stdout(), init.io, &stdout_buffer);
    const stdout = &stdout_file_writer.interface;

    // --- Step 2: read what the user typed. ---
    // args[0] is the program's own name; args[1] (if there is one) is the
    // number the user typed. Zig needs memory to store the list of
    // arguments, so we pass it an "allocator" (something that hands out
    // memory). The arena allocator cleans up automatically at the end.
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    // Use 10 unless the user typed a number.
    var how_many: u64 = 10;

    if (args.len > 2) {
        // Too many arguments: print a usage message to stderr and stop.
        std.debug.print("usage: zig run fibonacci.zig -- [how_many]\n", .{});
        std.process.exit(2);
    }

    if (args.len == 2) {
        // --- Step 3: turn the text (like "15") into a number. ---
        // parseInt gives back an error if the text isn't a whole number
        // that fits in a u64 (e.g. "abc" or "-3"). "catch" lets us handle
        // that error ourselves with a friendly message.
        how_many = std.fmt.parseInt(u64, args[1], 10) catch {
            std.debug.print("error: how_many must be a whole number, 0 or more (got '{s}')\n", .{args[1]});
            std.process.exit(2);
        };
    }

    // Check the number isn't too big for a u64 to hold the answer.
    if (how_many > max_how_many) {
        std.debug.print("error: how_many can be at most {d}\n", .{max_how_many});
        std.process.exit(2);
    }

    // --- Step 4: print each Fibonacci number, one per line. ---
    // This loop counts position = 0, 1, 2, ... up to (but not including)
    // how_many, just like `for position in range(how_many)` in Python.
    var position: u64 = 0;
    while (position < how_many) : (position += 1) {
        // {d} means "print this as a decimal number".
        // .{ ... } is the list of values to fill into the {} slots.
        try stdout.print("{d}\n", .{fibonacci(position)});
    }

    // Send anything still sitting in the buffer out to the terminal.
    // If we forget this, the last few lines might never appear!
    try stdout.flush();
}

// --- Tests ---
// Run these with:  zig test fibonacci.zig
// Each test checks that fibonacci() gives the answer we expect.
test "first few Fibonacci numbers" {
    try std.testing.expectEqual(@as(u64, 0), fibonacci(0));
    try std.testing.expectEqual(@as(u64, 1), fibonacci(1));
    try std.testing.expectEqual(@as(u64, 1), fibonacci(2));
    try std.testing.expectEqual(@as(u64, 2), fibonacci(3));
    try std.testing.expectEqual(@as(u64, 55), fibonacci(10));
}
