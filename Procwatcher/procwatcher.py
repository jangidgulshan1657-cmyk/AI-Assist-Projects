#!/usr/bin/env python3
"""procwatch.py - Tool 5 of the PC toolkit.

Every running program on Linux has a folder in /proc named after its
process ID (its PID). This script reads those folders and shows which
processes use the most memory and the most CPU.

This is the first tool written with TYPE HINTS: the ": int" and "-> str"
bits. They label what goes into a function and what comes out.
Python ignores them when it runs. Your editor and a tool called mypy
read them and catch mistakes before you run anything.

Usage:
    python3 procwatch.py              # top 8 in each list
    python3 procwatch.py --top 15     # more rows

It only READS. It never kills or changes anything.
"""

import os
import sys
import time
from dataclasses import dataclass

SAMPLE_SECONDS: float = 1.0  # how long we watch to measure CPU


@dataclass
class Proc:
    # A dataclass is a class where you only list the fields and their types.
    # Python writes __init__ for you.
    pid: int
    name: str
    memory_kb: int
    cpu_percent: float


def human_kb(kb: int) -> str:
    # Turns 1572864 (kB) into "1.5 GB"
    size: float = float(kb)
    for unit in ["KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size = size / 1024
    return f"{size:.1f} TB"


def list_pids() -> list[int]:
    # Every folder in /proc whose name is a number is a running process.
    pids: list[int] = []
    for entry in os.listdir("/proc"):
        if entry.isdigit():
            pids.append(int(entry))
    return pids


def read_cpu_ticks(pid: int) -> int | None:
    # "int | None" means: this returns a number, OR None if there is no answer.
    #
    # /proc/<pid>/stat is ONE long line like:  1234 (firefox) S 1 1234 ...
    # The name sits in brackets and can itself contain spaces or brackets,
    # so we cut at the LAST ")" and only split what comes after it.
    try:
        with open(f"/proc/{pid}/stat") as f:
            text = f.read()
    except OSError:
        return None  # the process ended while we were looking

    after_name = text.rsplit(")", 1)[1].split()
    utime = int(after_name[11])  # ticks spent running the program's own code
    stime = int(after_name[12])  # ticks spent in the kernel on its behalf
    return utime + stime


def read_name(pid: int) -> str:
    # /proc/<pid>/comm holds the program name. The kernel usually cuts it
    # at 15 letters, so long names look chopped (e.g. "Isolated Web Co").
    try:
        with open(f"/proc/{pid}/comm") as f:
            return f.read().strip()
    except OSError:
        return "?"


def read_memory_kb(pid: int) -> int:
    # /proc/<pid>/status has a line like "VmRSS:   123456 kB".
    # VmRSS = the RAM this process is holding right now.
    # Kernel threads have no such line, so they count as 0.
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1])
    except OSError:
        pass
    return 0


def take_sample() -> dict[int, int]:
    # One snapshot: PID -> total CPU ticks that process has used so far.
    sample: dict[int, int] = {}
    for pid in list_pids():
        ticks = read_cpu_ticks(pid)
        if ticks is not None:  # mypy forces this check: ticks could be None
            sample[pid] = ticks
    return sample


def build_list(before: dict[int, int], after: dict[int, int], seconds: float) -> list[Proc]:
    # CPU use = how many ticks it used BETWEEN the two snapshots,
    # divided by how many ticks the clock produced in that time.
    ticks_per_second: int = os.sysconf("SC_CLK_TCK")
    procs: list[Proc] = []
    for pid, ticks_now in after.items():
        ticks_then = before.get(pid, 0)  # started after snapshot 1? then it had 0
        cpu = (ticks_now - ticks_then) / (ticks_per_second * seconds) * 100
        procs.append(Proc(pid, read_name(pid), read_memory_kb(pid), max(cpu, 0.0)))
    return procs


def memory_of(p: Proc) -> int:
    return p.memory_kb


def cpu_of(p: Proc) -> float:
    return p.cpu_percent


def print_table(title: str, procs: list[Proc]) -> None:
    # "-> None" means: this function returns nothing, it only prints.
    print()
    print(f"=== {title} ===")
    print(f"  {'PID':>7}  {'NAME':<16} {'MEMORY':>9} {'CPU':>7}")
    for p in procs:
        # p.name[:16] keeps only the first 16 letters, so one long name
        # cannot push the other columns out of line.
        print(f"  {p.pid:>7}  {p.name[:16]:<16} {human_kb(p.memory_kb):>9} {p.cpu_percent:>6.1f}%")


def parse_top(args: list[str]) -> int:
    # Reads "--top N" from the command line. Default is 8.
    top = 8
    if "--top" in args:
        index = args.index("--top")
        try:
            top = int(args[index + 1])
        except (IndexError, ValueError):
            print("--top needs a number, for example: --top 15")
            sys.exit(1)  # exit code 1 = "something went wrong"
        if top < 1:
            print("--top must be 1 or more")
            sys.exit(1)
    return top

def parse_sort(args: list[str])-> str:
    sort = "cpu"

    if "--sort" in args:
        index = args.index("--sort")
        try:
            sort = args[index + 1]
        except IndexError:
            print("--sort needs cpu | mem")
            sys.exit(1)
        if sort not in  ("cpu","mem"):
            print(f"Invalid sort option '{sort}'. Use 'mem' or 'cpu'")
            sys.exit(1)
    return sort

def main() -> None:
    args = sys.argv[1:]
    top = parse_top(args)

    print(f"Measuring CPU for {SAMPLE_SECONDS:.0f} second ...")
    before = take_sample()
    start = time.monotonic()
    time.sleep(SAMPLE_SECONDS)
    after = take_sample()
    elapsed = time.monotonic() - start

    procs = build_list(before, after, elapsed)
    print(f"{len(procs)} processes running. 100% CPU = one full core.")

    by_memory = sorted(procs, key=memory_of, reverse=True)
    by_cpu = sorted(procs, key=cpu_of, reverse=True)

    sort = parse_sort(args)
    if sort == "cpu":
        print_table(f"TOP {top} BY CPU (measured over {elapsed:.1f}s)", by_cpu[:top])
    else:
        print_table(f"TOP {top} BY MEMORY", by_memory[:top])


    print()
    print("Memory is RSS: RAM each process holds. Shared memory is counted in")
    print("every process that uses it, so the rows do not add up to your total RAM.")


if __name__ == "__main__":
    main()