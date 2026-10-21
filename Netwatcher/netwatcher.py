#!/usr/bin/env python3
"""netwatch.py - Tool 6 of the PC toolkit.

How fast is data flowing in and out of this PC right now?

The kernel keeps a running total of bytes sent and received for every
network interface in /proc/net/dev. The totals only ever go up, so one
look tells you nothing about speed. Look twice, one second apart,
and the difference IS the speed. (Same trick as procwatch.py.)

Usage:
    python3 netwatch.py

It only READS. It never changes anything.
"""
import sys
import time

SAMPLE_SECONDS: float = 1.0


def read_counters() -> dict[str, tuple[int, int]]:
    # Returns  interface name -> (bytes received, bytes sent)  since boot.
    #
    # /proc/net/dev looks like this (the first two lines are headers):
    #   eth0: 987654321 8000 0 0 0 0 0 0 123456789 6000 0 0 0 0 0 0
    # After the name come 8 "receive" numbers, then 8 "send" numbers.
    # Bytes are the first of each group: position 0 and position 8.
    counters: dict[str, tuple[int, int]] = {}
    with open("/proc/net/dev") as f:
        lines = f.readlines()

    for line in lines[2:]:
        name, rest = line.split(":", 1)  # cut at the first ":" only
        numbers = rest.split()
        counters[name.strip()] = (int(numbers[0]), int(numbers[8]))
    return counters


def human(n_bytes: float) -> str:
    # Turns 1572864 into "1.5 MB"
    size = n_bytes
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size = size / 1024
    return f"{size:.1f} TB"

def parse_watch(args:list[str])->int | None:
    if "--watch" not in args:
        return None
    watch = 0
    if "--watch" in args:
        index = args.index("--watch")
        try:
            watch = int(args[index + 1])
        except (IndexError,ValueError):
            print("--watch requires a whole number of seconds (e.g., --watch 2")
            sys.exit(1)
        if watch < 1:
            print("--watch interval must be at least 1 second")
            sys.exit(1)
    return watch

def main() -> None:
    args = sys.argv[1:]
    watcher = parse_watch(args)
    interval = float(watcher) if watcher else SAMPLE_SECONDS

    try:
        before = read_counters()
        start = time.monotonic()
        hig_down = float(0.0)
        while True:
            time.sleep(interval)
            after = read_counters()
            now = time.monotonic()
            elapsed = now - start
            
            if watcher is not None:
                print("\033[2J\033[H", end="")
            print(f"Measuring for {interval:.0f} second ...")

            print()
            print(f"=== NETWORK (measured over {elapsed:.1f}s) ===")
            print(f"  {'INTERFACE':<14} {'DOWN/s':>11} {'UP/s':>11} {'TOTAL DOWN':>12} {'TOTAL UP':>10}")

            for name in after:
                rx_now, tx_now = after[name]
                # If the interface appeared during our second, there is no "before".
                rx_then, tx_then = before.get(name, (rx_now, tx_now))

                # max(..., 0): the kernel resets a counter if an interface restarts.
                down = max(rx_now - rx_then, 0) / elapsed
                up = max(tx_now - tx_then, 0) / elapsed

                print(
                    f"  {name:<14} {human(down) + '/s':>11} {human(up) + '/s':>11}"
                    f" {human(rx_now):>12} {human(tx_now):>10}"
                )

            if down > hig_down:
                hig_down = down
            print(f"\n{human(hig_down)}/s is the Highest download Speed!!")

            print()
            print("DOWN = received, UP = sent. TOTAL = since this PC booted.")
            print("lo is the loopback: traffic that never leaves your own PC.")

            if not watcher:
                break
             
            before = after
            start = now
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()