#!/usr/bin/env python3
"""sysinfo.py - Tool 1 of the PC toolkit.

Linux keeps live system facts in plain text files under /proc.
This script just opens those files, pulls out numbers, and prints them.

Usage:
    python3 sysinfo.py                 # checks / and /home
    python3 sysinfo.py /mnt/hdd        # also checks another mount point
"""

import os
import shutil
import sys


def read_uptime():
    # /proc/uptime looks like: "12345.67 98765.43"
    # The first number is seconds since boot.
    with open("/proc/uptime") as f:
        text = f.read()
    seconds = float(text.split()[0])

    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{days}d {hours}h {minutes}m"


def read_cpu_model():
    # /proc/cpuinfo has many lines like "model name : Intel(R) ..."
    # We only want the first line that starts with "model name".
    with open("/proc/cpuinfo") as f:
        for line in f:
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    return "unknown"

def read_distro():
    with open("/etc/os-release") as f:
        for line in f:
            if line.startswith("PRETTY_NAME="):
                return line.split("=",1)[1].strip().strip("'\"")
    return "unknown"

def read_load():
    # /proc/loadavg looks like: "0.52 0.48 0.40 1/523 8841"
    # First three numbers: average load over 1, 5, 15 minutes.
    with open("/proc/loadavg") as f:
        parts = f.read().split()
    return parts[0], parts[1], parts[2]


def read_memory():
    # /proc/meminfo has lines like "MemTotal:   16318420 kB"
    # We store every line in a dictionary, then pick what we need.
    info = {}
    with open("/proc/meminfo") as f:
        for line in f:
            name, rest = line.split(":")
            info[name] = int(rest.split()[0])  # number in kB

    total = info["MemTotal"]
    available = info["MemAvailable"]  # what programs could still use
    used = total - available
    return total, used


def bar(percent, width=20):
    # Turns 60 into "############--------"
    filled = int(percent / 100 * width)
    return "#" * filled + "-" * (width - filled)


def show_disk(path):
    # shutil.disk_usage asks the OS about the disk that holds `path`.
    if not os.path.exists(path):
        print(f"  {path:<12} (does not exist)")
        return
    total, used, free = shutil.disk_usage(path)
    percent = used / total * 100
    total_gb = total / 1024**3
    used_gb = used / 1024**3
    print(f"  {path:<12} [{bar(percent)}] {percent:4.1f}%  {used_gb:.0f} / {total_gb:.0f} GB")


def main():
    print("=== SYSTEM INFO ===")
    print(f"Distro: {read_distro()}")
    print(f"Uptime : {read_uptime()}")
    print(f"CPU    : {read_cpu_model()} ({os.cpu_count()} threads)")

    one, five, fifteen = read_load()
    print(f"Load   : {one} (1m)  {five} (5m)  {fifteen} (15m)")

    total_kb, used_kb = read_memory()
    mem_percent = used_kb / total_kb * 100
    total_gb = total_kb / 1024 / 1024
    used_gb = used_kb / 1024 / 1024
    print(f"RAM    : [{bar(mem_percent)}] {mem_percent:4.1f}%  {used_gb:.1f} / {total_gb:.1f} GB")

    print("Disks  :")
    paths = ["/"]
    paths = paths + sys.argv[1:]  # extra mount points from the command line
    for path in paths:
        show_disk(path)


main()