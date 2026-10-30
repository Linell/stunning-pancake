//! Fibonacci numbers computed with recursion.
//!
//!     F(0) = 0, F(1) = 1, F(n) = F(n-1) + F(n-2)
//!
//! The recursion follows that definition directly and is memoized, so each
//! F(k) is computed once (linear time instead of exponential).
//!
//! Usage:
//!     zig run fib.zig -- COUNT       print F(0) .. F(COUNT-1), one per line
//!     zig run fib.zig -- --nth N     print F(N) only
//!     zig test fib.zig               run the tests below
//!
//! Values are u128, so the largest index is 186 (F(187) does not fit).
//! Exit codes: 0 success, 1 could not write output, 2 usage error.
//! Standard library only; written for Zig 0.14 and 0.15.

const std = @import("std");

/// Largest n for which F(n) fits in a u128.
pub const max_n: u8 = 186;

pub const FibError = error{Overflow};

const Memo = [max_n + 1]?u128;

fn emptyMemo() Memo {
    return [_]?u128{null} ** (max_n + 1);
}

/// The recursive definition. Depth is at most n (<= 186), and memoization
/// means each F(k) is added up only once.
fn fibMemo(n: u8, memo: *Memo) u128 {
    if (n < 2) return n;
    if (memo[n]) |cached| return cached;
    const value = fibMemo(n - 1, memo) + fibMemo(n - 2, memo);
    memo[n] = value;
    return value;
}

/// Returns F(n), or error.Overflow if n > max_n.
pub fn fib(n: u64) FibError!u128 {
    if (n > max_n) return error.Overflow;
    var memo = emptyMemo();
    return fibMemo(@intCast(n), &memo);
}

/// Fills `out` with F(0), F(1), ..., F(out.len - 1).
/// Returns error.Overflow (leaving `out` untouched) if out.len > max_n + 1.
pub fn fibSequence(out: []u128) FibError!void {
    if (out.len > @as(usize, max_n) + 1) return error.Overflow;
    var memo = emptyMemo();
    for (out, 0..) |*slot, k| slot.* = fibMemo(@intCast(k), &memo);
}

// --- command line ----------------------------------------------------------

pub const usage =
    \\usage: fib COUNT
    \\       fib --nth N
    \\  COUNT          print F(0) .. F(COUNT-1), one per line (COUNT <= 187)
    \\  -n, --nth N    print only F(N) (N <= 186)
    \\  -h, --help     show this message
    \\
;

const ParseError = error{ Invalid, TooLarge };

/// Parses a non-negative decimal integer made of ASCII digits only.
/// Rejects "", "+3", " 3", "1_000", "-3" and non-ASCII digits such as "٣".
/// Values above 1000 are reported as TooLarge (never overflows).
fn parseIndex(text: []const u8) ParseError!u64 {
    if (text.len == 0) return error.Invalid;
    var value: u64 = 0;
    var too_large = false;
    for (text) |c| {
        if (c < '0' or c > '9') return error.Invalid;
        if (!too_large) {
            value = value * 10 + (c - '0');
            if (value > 1000) too_large = true;
        }
    }
    if (too_large) return error.TooLarge;
    return value;
}

pub const Result = struct {
    code: u8,
    out: []const u8,
    err: []const u8,
};

/// Big enough for the largest output (F(0)..F(186) is 3851 bytes).
pub const out_buf_len = 8192;
pub const err_buf_len = 1024;

fn usageError(err_buf: []u8, comptime fmt: []const u8, args: anytype) Result {
    const msg: []const u8 = std.fmt.bufPrint(err_buf, "fib: " ++ fmt ++ "\n" ++ usage, args) catch
        // The offending argument was too long to echo back.
        "fib: invalid argument\n" ++ usage;
    return .{ .code = 2, .out = "", .err = msg };
}

fn isHelp(arg: []const u8) bool {
    return std.mem.eql(u8, arg, "-h") or std.mem.eql(u8, arg, "--help");
}

fn isNth(arg: []const u8) bool {
    return std.mem.eql(u8, arg, "-n") or std.mem.eql(u8, arg, "--nth");
}

/// Runs the CLI on `args` (program name excluded) without doing any I/O.
/// `out` and `err` in the result point into `out_buf` / `err_buf` or static text.
pub fn run(args: []const []const u8, out_buf: []u8, err_buf: []u8) Result {
    for (args) |arg| {
        if (isHelp(arg)) return .{ .code = 0, .out = usage, .err = "" };
    }
    if (args.len == 0) return usageError(err_buf, "expected COUNT or --nth N", .{});

    // Work out which mode we are in and which argument holds the number.
    var nth_mode = false;
    var number: []const u8 = undefined;
    const first = args[0];
    if (isNth(first)) {
        if (args.len < 2) return usageError(err_buf, "{s} needs a value", .{first});
        if (args.len > 2) return usageError(err_buf, "unexpected argument '{s}'", .{args[2]});
        nth_mode = true;
        number = args[1];
    } else if (std.mem.startsWith(u8, first, "--nth=")) {
        if (args.len > 1) return usageError(err_buf, "unexpected argument '{s}'", .{args[1]});
        nth_mode = true;
        number = first["--nth=".len..];
    } else {
        const looks_negative = first.len > 1 and first[0] == '-' and
            first[1] >= '0' and first[1] <= '9';
        if (first.len > 1 and first[0] == '-' and !looks_negative)
            return usageError(err_buf, "unknown option '{s}'", .{first});
        if (args.len > 1) return usageError(err_buf, "unexpected argument '{s}'", .{args[1]});
        number = first;
    }

    const limit: u64 = if (nth_mode) max_n else @as(u64, max_n) + 1;
    const name: []const u8 = if (nth_mode) "N" else "COUNT";
    const value = parseIndex(number) catch |e| switch (e) {
        error.Invalid => return usageError(err_buf, "{s} must be a non-negative integer, got '{s}'", .{ name, number }),
        error.TooLarge => return usageError(err_buf, "{s} must be at most {d}, got '{s}'", .{ name, limit, number }),
    };
    if (value > limit)
        return usageError(err_buf, "{s} must be at most {d}, got '{s}'", .{ name, limit, number });

    var values_buf: [max_n + 1]u128 = undefined;
    const values: []u128 = if (nth_mode) blk: {
        values_buf[0] = fib(value) catch unreachable; // value <= max_n checked above
        break :blk values_buf[0..1];
    } else blk: {
        const count: usize = @intCast(value);
        const seq = values_buf[0..count];
        fibSequence(seq) catch unreachable; // value <= max_n + 1 checked above
        break :blk seq;
    };

    var len: usize = 0;
    for (values) |v| {
        const line = std.fmt.bufPrint(out_buf[len..], "{d}\n", .{v}) catch
            return .{ .code = 2, .out = "", .err = "fib: internal error: output buffer too small\n" };
        len += line.len;
    }
    return .{ .code = 0, .out = out_buf[0..len], .err = "" };
}

// std.io.getStdOut() was replaced by std.fs.File.stdout() in Zig 0.15; only
// the branch that exists in the running Zig version is compiled.
fn stdoutFile() std.fs.File {
    return if (comptime @hasDecl(std.fs.File, "stdout")) std.fs.File.stdout() else std.io.getStdOut();
}

fn stderrFile() std.fs.File {
    return if (comptime @hasDecl(std.fs.File, "stderr")) std.fs.File.stderr() else std.io.getStdErr();
}

pub fn main() u8 {
    const allocator = std.heap.page_allocator;
    const argv = std.process.argsAlloc(allocator) catch {
        stderrFile().writeAll("fib: out of memory reading arguments\n") catch {};
        return 2;
    };
    defer std.process.argsFree(allocator, argv);

    const skip: usize = if (argv.len > 0) 1 else 0; // program name
    const args = allocator.alloc([]const u8, argv.len - skip) catch {
        stderrFile().writeAll("fib: out of memory reading arguments\n") catch {};
        return 2;
    };
    defer allocator.free(args);
    for (args, argv[skip..]) |*dst, src| dst.* = src;

    var out_buf: [out_buf_len]u8 = undefined;
    var err_buf: [err_buf_len]u8 = undefined;
    const result = run(args, &out_buf, &err_buf);

    stderrFile().writeAll(result.err) catch {};
    stdoutFile().writeAll(result.out) catch {
        stderrFile().writeAll("fib: could not write output\n") catch {};
        return if (result.code == 0) 1 else result.code;
    };
    return result.code;
}

// --- tests -----------------------------------------------------------------

const testing = std.testing;

const first_20 = [_]u128{ 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181 };

test "base cases" {
    try testing.expectEqual(@as(u128, 0), try fib(0));
    try testing.expectEqual(@as(u128, 1), try fib(1));
}

test "first 20 values" {
    for (first_20, 0..) |expected, n| try testing.expectEqual(expected, try fib(n));
}

test "known large values" {
    try testing.expectEqual(@as(u128, 12586269025), try fib(50));
    try testing.expectEqual(@as(u128, 354224848179261915075), try fib(100));
    // Last value that fits in u64, and the first that doesn't.
    try testing.expectEqual(@as(u128, 12200160415121876738), try fib(93));
    try testing.expectEqual(@as(u128, 19740274219868223167), try fib(94));
    // Last value that fits in u128.
    try testing.expectEqual(@as(u128, 332825110087067562321196029789634457848), try fib(186));
}

test "recurrence holds for every supported n" {
    var n: u64 = 2;
    while (n <= max_n) : (n += 1) {
        try testing.expectEqual((try fib(n - 1)) + (try fib(n - 2)), try fib(n));
    }
}

test "indices past 186 overflow instead of wrapping" {
    try testing.expectError(error.Overflow, fib(187));
    try testing.expectError(error.Overflow, fib(1000));
    try testing.expectError(error.Overflow, fib(std.math.maxInt(u64)));
}

test "fibSequence: empty" {
    var none: [0]u128 = .{};
    try fibSequence(&none);
}

test "fibSequence: first 20" {
    var seq: [20]u128 = undefined;
    try fibSequence(&seq);
    try testing.expectEqualSlices(u128, &first_20, &seq);
}

test "fibSequence: longest supported matches fib" {
    var seq: [max_n + 1]u128 = undefined;
    try fibSequence(&seq);
    for (seq, 0..) |v, k| try testing.expectEqual(try fib(k), v);
}

test "fibSequence: too long overflows and leaves output untouched" {
    var seq = [_]u128{7} ** (max_n + 2);
    try testing.expectError(error.Overflow, fibSequence(&seq));
    for (seq) |v| try testing.expectEqual(@as(u128, 7), v);
}

test "parseIndex accepts plain ASCII digits" {
    try testing.expectEqual(@as(u64, 0), try parseIndex("0"));
    try testing.expectEqual(@as(u64, 7), try parseIndex("007"));
    try testing.expectEqual(@as(u64, 186), try parseIndex("186"));
    try testing.expectEqual(@as(u64, 1000), try parseIndex("1000"));
}

test "parseIndex rejects malformed input" {
    const bad = [_][]const u8{ "", "+3", " 3", "3 ", "1_000", "-3", "3x", "0x10", "1.5", "\u{0663}", "\u{FF13}" };
    for (bad) |text| try testing.expectError(error.Invalid, parseIndex(text));
}

test "parseIndex reports huge numbers without overflowing" {
    try testing.expectError(error.TooLarge, parseIndex("1001"));
    try testing.expectError(error.TooLarge, parseIndex("18446744073709551616"));
    try testing.expectError(error.TooLarge, parseIndex("9" ** 100));
    // Validation continues past the point where the value got too large.
    try testing.expectError(error.Invalid, parseIndex("99999x"));
}

fn runArgs(args: []const []const u8) Result {
    const S = struct {
        var out: [out_buf_len]u8 = undefined;
        var err: [err_buf_len]u8 = undefined;
    };
    return run(args, &S.out, &S.err);
}

fn expectUsageError(args: []const []const u8, needle: []const u8) !void {
    const r = runArgs(args);
    try testing.expectEqual(@as(u8, 2), r.code);
    try testing.expectEqualStrings("", r.out);
    try testing.expect(std.mem.startsWith(u8, r.err, "fib: "));
    try testing.expect(std.mem.indexOf(u8, r.err, needle) != null);
    try testing.expect(std.mem.endsWith(u8, r.err, usage));
}

test "run: COUNT prints the sequence" {
    const r = runArgs(&.{"10"});
    try testing.expectEqual(@as(u8, 0), r.code);
    try testing.expectEqualStrings("0\n1\n1\n2\n3\n5\n8\n13\n21\n34\n", r.out);
    try testing.expectEqualStrings("", r.err);
}

test "run: COUNT 0 and 1" {
    var r = runArgs(&.{"0"});
    try testing.expectEqual(@as(u8, 0), r.code);
    try testing.expectEqualStrings("", r.out);
    r = runArgs(&.{"1"});
    try testing.expectEqualStrings("0\n", r.out);
}

test "run: largest COUNT fits the output buffer" {
    const r = runArgs(&.{"187"});
    try testing.expectEqual(@as(u8, 0), r.code);
    try testing.expectEqual(@as(usize, 3851), r.out.len);
    try testing.expect(std.mem.endsWith(u8, r.out, "\n332825110087067562321196029789634457848\n"));
}

test "run: --nth, -n and --nth=" {
    var r = runArgs(&.{ "--nth", "100" });
    try testing.expectEqual(@as(u8, 0), r.code);
    try testing.expectEqualStrings("354224848179261915075\n", r.out);
    r = runArgs(&.{ "-n", "0" });
    try testing.expectEqualStrings("0\n", r.out);
    r = runArgs(&.{"--nth=7"});
    try testing.expectEqualStrings("13\n", r.out);
    r = runArgs(&.{ "--nth", "186" });
    try testing.expectEqualStrings("332825110087067562321196029789634457848\n", r.out);
}

test "run: help" {
    for ([_][]const u8{ "-h", "--help" }) |flag| {
        const args = [_][]const u8{flag};
        const r = runArgs(&args);
        try testing.expectEqual(@as(u8, 0), r.code);
        try testing.expectEqualStrings(usage, r.out);
        try testing.expectEqualStrings("", r.err);
    }
}

test "run: usage errors" {
    try expectUsageError(&[_][]const u8{}, "expected COUNT or --nth N");
    try expectUsageError(&.{"188"}, "COUNT must be at most 187, got '188'");
    try expectUsageError(&.{"99999999999999999999999"}, "at most 187");
    try expectUsageError(&.{ "--nth", "187" }, "N must be at most 186, got '187'");
    try expectUsageError(&.{"--nth=187"}, "at most 186");
    try expectUsageError(&.{"--nth"}, "--nth needs a value");
    try expectUsageError(&.{"-n"}, "-n needs a value");
    try expectUsageError(&.{"--nth="}, "N must be a non-negative integer, got ''");
    try expectUsageError(&.{ "--nth", "3", "4" }, "unexpected argument '4'");
    try expectUsageError(&.{ "--nth=3", "4" }, "unexpected argument '4'");
    try expectUsageError(&.{ "1", "2" }, "unexpected argument '2'");
    try expectUsageError(&.{"--bogus"}, "unknown option '--bogus'");
    try expectUsageError(&.{"-3"}, "COUNT must be a non-negative integer, got '-3'");
    try expectUsageError(&.{"-"}, "got '-'");
    try expectUsageError(&.{""}, "got ''");
    try expectUsageError(&.{"abc"}, "got 'abc'");
    try expectUsageError(&.{"\u{0663}"}, "got '\u{0663}'");
    try expectUsageError(&.{ "--nth", "\u{1F415}" }, "got '\u{1F415}'");
}

test "run: argument too long to echo still gives a usage error" {
    const long = "x" ** 2000;
    try expectUsageError(&.{long}, "fib: invalid argument");
}
