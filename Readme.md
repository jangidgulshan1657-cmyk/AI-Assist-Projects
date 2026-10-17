# AI Assist Projects

Small, real programs I build together with an AI pair-programmer (Claude, by Anthropic) to learn Python and Linux. I don't do abstract drills. I read working code, run it on my own machine, and then change it myself.

I'm self-taught. This repo is my learning log, and every project in it runs on my own PC (Fedora 44 with Hyprland) and does something I actually use.

## How the work goes

1. We pick a small project that is useful or fun.
2. Claude writes a complete, working version and explains it in plain language.
3. I read it, run it on my own PC, and make at least one real modification myself.
4. I paste my full code and the real terminal output back for blunt review. Bugs found in review get fixed, and the lesson goes in the [Lessons](#lessons-from-real-bugs) section.

**On AI use:** the first version of each tool is AI-written. The modifications, the fixes and the testing on my own machine are mine, and each tool below lists what I changed.

**Rules every tool follows:**

- It runs on my real machine.
- It prints something I can see.
- It teaches one new idea.
- It is safe by default: read-only, or a dry-run until I pass `--run`.

## Linux PC toolkit

A set of small tools for my own Linux machine. Each one builds on the one before, and later they get wired into my Hyprland desktop.

| # | Tool | What it does | Idea it teaches | Status |
|---|------|--------------|-----------------|--------|
| 1 | `sysinfo.py` | Shows distro, uptime, CPU, load, RAM and disk usage | Linux exposes system state as plain files (`/proc`) | Done |
| 2 | `diskhog.py` | Finds which folders and files are eating the disk | Walking the filesystem with `os.walk`, and why symlinks are skipped | Done |
| 3 | Downloads organizer (`folderorganizer.py`) | Sorts files in Downloads into folders by type | Moving files safely, with a dry-run first | Done |
| 4 | `watcher.py` | Sorts new files the moment they finish downloading | Polling, and waiting for a file to finish writing | Built and tested, my modifications in progress |
| 5 | `procwatch.py` | Lists running processes and the heavy ones | Processes as folders in `/proc` | Planned |
| 6 | `hypr.py` | Talks to Hyprland through `hyprctl` | Reading JSON from another program | Planned |
| 7 | Waybar module | Shows tools 1, 2 and 5 live in the top bar | Connecting tools into one desktop | Planned |
| 8 | systemd timer | Runs a tool automatically with no terminal | Services and timers | Planned |
| 9 | Jarvis hook | Lets an LLM call these tools from plain English | Letting a model choose a tool | Planned |

The thread running through all of them is read, format, show, ask.

### `sysinfo.py`

```
python3 sysinfo.py                 # checks / and /home
python3 sysinfo.py /mnt/hdd        # also checks another mount point
```

```
=== SYSTEM INFO ===
Distro: Fedora Linux 44 (Workstation Edition)
Uptime : 0d 0h 44m
CPU    : AMD Ryzen 5 4600G with Radeon Graphics (12 threads)
Load   : 0.19 (1m)  0.35 (5m)  0.35 (15m)
RAM    : [######--------------] 31.6%  4.9 / 15.4 GB
Disks  :
  /            [###########---------] 56.9%  134 / 236 GB
  /home        [###########---------] 56.9%  134 / 236 GB
```

**My changes:** added the distro line (`read_distro()` reading `/etc/os-release`).

### `diskhog.py`

Read-only. It never changes or deletes anything.

```
python3 diskhog.py                 # scans your home folder
python3 diskhog.py /mnt/hdd1       # scans any folder you give it
```

```
=== BIGGEST ITEMS IN /home/gulshan (total 48.1 GB) ===
  [########------------] 42.1%    20.3 GB  Videos                   282 Files
  [###-----------------] 18.9%     9.1 GB  Pictures                4076 Files
  [##------------------] 13.2%     6.4 GB  .cache                185790 Files
```

**My changes:** added a file count per folder, and fixed a bug found in review (see Lessons).

### `watcher.py`

Dry-run by default: it only prints what it would do. Add `--run` to really move files.

```
python3 watcher.py                 # watch ~/Downloads, dry-run
python3 watcher.py --run           # watch ~/Downloads, really move new files
python3 watcher.py /some/folder    # watch another folder
```

Files already in the folder when it starts are ignored. Only new arrivals are touched. Example from a test with simulated downloads (not my real Downloads folder):

```
03:00:57  MOVED  photo.png  ->  Pictures/
03:00:57  SKIP   dup.png  (already a file with that name in Pictures/)
03:01:01  MOVED  movie.mkv  ->  Videos/
```

**My changes:** in progress.

## Earlier projects

- **Downloads organizer:** sorts a folder by file type. It is dry-run by default, takes `--run`, and skips hidden files and name clashes.
- **Terminal Wordle:** loads words from `words.json`, validates guesses, and shows coloured feedback.
- **Taskmanager (CLI):** tasks, a weather risk check, config, and LLM command dispatch through Groq. Still in progress.

## Requirements

- Linux (`sysinfo.py` reads `/proc`).
- Python 3. The toolkit uses only the standard library, so there is nothing to `pip install`.

```
git clone https://github.com/gulshan/<repo-name>.git
cd <repo-name>/Linux
python3 sysinfo.py
```

## Lessons from real bugs

- **Run tools from a real terminal, not a sandboxed one.** `sysinfo.py` once reported the wrong distro and an 8 GB root disk. I was running it from a Flatpak terminal, which sees the Flatpak runtime's files instead of the real system.
- **Set a variable on every path through the code.** In `diskhog.py`, a loose file never set its file count, so it showed the previous folder's count or crashed with `UnboundLocalError`. Whenever an `if` sets a value, check what the `else` does.
- **A file that exists isn't a file that's finished.** `watcher.py` waits until a file's size stops changing and ignores `.crdownload` and `.part`, so it never moves a half-downloaded file.
- **A tool with no dry-run is a tool that eventually deletes the wrong thing.** Anything that moves files starts as a dry-run.

## Roadmap

Rows 5 to 9 in the toolkit table above, in that order. Each tool must reuse something from the one before it.