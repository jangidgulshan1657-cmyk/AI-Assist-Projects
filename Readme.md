# AI Assist Projects

A set of small Python programs for my own Linux PC, built together with an AI
pair-programmer (Claude, by Anthropic), ending with a small AI agent that runs
them. I'm self-taught, and this repo is my learning log: I read working code,
run it on my own machine, and then change it myself.

**Status: finished.** The toolkit and the agent work. New, useful agents will
start in their own projects.

## How it was built

1. Pick a small project that is useful or fun.
2. Claude writes a complete working version and explains it in plain language.
3. I read it, run it on my PC, and make my own modifications.
4. I paste my full code and the real terminal output back for blunt review.
   Bugs found that way are listed under [Lessons](#lessons-from-real-bugs).

**On AI use:** the first version of each tool was written by Claude. The
modifications, the testing on my own machine and the fixes are mine. The
"My changes" column below says what I changed in each one.

**Rules every tool follows:** it runs on my real machine, prints something I can
see, teaches one new idea, and is safe by default (read-only, or a dry-run
until I pass `--run`).

## What's inside

| Tool | What it does | Idea it teaches | My changes |
|------|--------------|-----------------|------------|
| `Linux/sysinfo.py` | Distro, uptime, CPU, load, RAM, disk usage | Linux exposes system state as files (`/proc`) | Added the distro line |
| `Linux/diskhog.py` | Biggest folders and files, with file counts | Walking the filesystem with `os.walk`; why symlinks are skipped | File count per folder; fixed a stale-variable bug |
| Downloads organizer | Sorts Downloads into folders by file type | Moving files safely, dry-run first | Written in an earlier session |
| `Watcher/` | Sorts new files as soon as they finish downloading | Polling; waiting for a file to stop growing | More categories, `--every`, log file, desktop notifications, session summary |
| `Procwatcher/procwatcher.py` | Busiest processes by CPU or memory | One folder per process in `/proc`; two snapshots give a rate; type hints | Owner column, process-state counts, `--sort`, `--watch` |
| `Netwatcher/netwatcher.py` | Download and upload speed per network interface | `/proc/net/dev` counters; rates from two snapshots | `--watch`, peak download speed |
| `AI-Assistent/jarvis.py` | An agent that answers questions by running the tools above | The agent loop; letting an LLM choose a tool safely | See below |

Folder names are as in my repo. They may differ slightly from yours.

Earlier projects from before the toolkit: a terminal Wordle and a CLI
Taskmanager (tasks, weather risk, config, LLM command dispatch through Groq).

**Planned but never built:** a Hyprland tool, a Waybar module and a scheduled
timer. The repo ended before them.

## Jarvis

```
you ask -> LLM picks a tool -> Jarvis runs it -> LLM reads the output -> answer
```

That loop is what an agent is. Jarvis shows the LLM a menu of four tools
(`system_info`, `disk_hogs`, `processes`, `network`). The LLM answers with a
tool name, Jarvis runs that script and sends the output back, and the LLM
explains it in plain words. A step limit stops runaway loops.

**Safety comes from the structure, not from trusting the model:**

- The LLM can only return a tool name from a fixed table.
- Jarvis turns that name into a fixed script path. The LLM never writes a command.
- Every tool only reads. Nothing is moved or deleted.
- Tool output is treated as data, not instructions.

### Run it

```
export GROQ_API_KEY="your-key"
python3 AI-Assistent/jarvis.py
```

The key comes from the environment and is never written into the code. The
default model is `llama-3.3-70b-versatile`; change it with `JARVIS_MODEL`.
Python's standard library only, so there is nothing to install. Tool paths are
set in the `TOOLS` table at the top of the file.

### A real session (mine, on my PC)

```
Jarvis is ready. Tools: system_info, disk_hogs, processes, network. Type 'exit' to quit.

You> ohk chech which file is taking up the most space
  [running disk_hogs ...]
Jarvis> The largest single file in your home directory is:

**/home/gulshan/Downloads/Disk Images/MX-25.2_July_x64.iso – 2.7 GB**.
```

### Known limits (found by actually using it)

- **A tool must match the question.** I asked which task uses the most RAM.
  Jarvis answered from the `processes` tool, which Jarvis runs with no
  arguments, so it is sorted by CPU and shows only the top 8. The answer was
  really "most RAM among the 8 busiest processes". Next time: give the agent a
  tool, or a validated argument, that matches the question (for example
  `--sort mem`).
- **It sees only what the process sees.** Launched from a Flatpak editor
  terminal, the process tools see only the sandbox, not the whole PC. The
  `com.vscodium.co` answer in my session looks like that case. Run it from a
  normal terminal.
- **Unclear input still reaches the model.** I typed `auit` instead of `quit`.
  It was not recognised as an exit command, so the model ran `system_info`.
  Harmless here because every tool is read-only.
- **Not built:** a cap on conversation history, a confirmation step before any
  risky action, tools that take arguments.
- Small issues from the AI review sessions may remain in individual tools.
  Check the code before relying on any of it.

## Requirements

- Linux. The tools read `/proc`.
- Python 3, standard library only. Developed on Fedora.
- A Groq API key for Jarvis only.

## Lessons from real bugs

- **Run tools from a real terminal, not a sandboxed one.** `sysinfo.py` once
  reported the wrong distro and an 8 GB root disk because I ran it from a
  Flatpak terminal.
- **Set a variable on every path through the code.** In `diskhog.py`, a loose
  file never set its file count and showed the previous folder's count. A
  variable after a loop holds only the last round's value.
- **A file that exists isn't a file that's finished.** The watcher waits until
  a file's size stops changing, and ignores `.crdownload` and `.part`.
- **Anything that moves files starts as a dry-run.**
- **A running total is not a speed.** Read it twice and divide the difference by
  the time. That is how CPU use and network speed both work.
- **Type hints are ignored by Python at runtime.** `mypy` reads them and catches
  mistakes, including a forgotten `None` check.
- **An agent is only as good as its tools.** The RAM question above was answered
  confidently from the wrong data.

## What's next

Useful agents, in new projects. What I carry over from this one: a
confirmation step before any risky action, validated tool arguments, a cap on
conversation history, and answers that name which tool they came from.