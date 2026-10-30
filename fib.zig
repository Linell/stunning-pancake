const std = @import("std");

const max_n = 186;

fn fib(n: u8, memo: *[max_n + 1]?u128) u128 {
    if (memo[n]) |v| return v;
    const v: u128 = if (n < 2) n else fib(n - 1, memo) + fib(n - 2, memo);
    memo[n] = v;
    return v;
}

fn usage() u8 {
    std.debug.print("usage: fib [-s] N   (0 <= N <= {d})\n", .{max_n});
    return 2;
}

pub fn main() !u8 {
    var gpa: std.heap.GeneralPurposeAllocator(.{}) = .init;
    defer _ = gpa.deinit();
    const args = try std.process.argsAlloc(gpa.allocator());
    defer std.process.argsFree(gpa.allocator(), args);

    var seq = false;
    var arg: ?[]const u8 = null;
    for (args[1..]) |a| {
        if (std.mem.eql(u8, a, "-s") or std.mem.eql(u8, a, "--sequence")) {
            seq = true;
        } else if (arg == null) {
            arg = a;
        } else return usage();
    }
    const n = std.fmt.parseInt(u8, arg orelse return usage(), 10) catch return usage();
    if (n > max_n) return usage();

    var memo: [max_n + 1]?u128 = @splat(null);
    const out = std.io.getStdOut().writer();
    if (seq) {
        for (0..n) |i| try out.print("{d}\n", .{fib(@intCast(i), &memo)});
    } else {
        try out.print("{d}\n", .{fib(n, &memo)});
    }
    return 0;
}
