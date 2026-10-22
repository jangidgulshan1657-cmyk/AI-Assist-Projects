import subprocess, sys

ok = subprocess.run([sys.executable, "-c", "print('hello')"],
                    capture_output=True, text=True)
print(repr(ok.stdout), ok.returncode)

bad = subprocess.run([sys.executable, "-c", "1/0"],
                     capture_output=True, text=True)
print(bad.returncode)
print(bad.stderr)

print("abcdefgh"[:3])

code = "import sys; print('to stdout'); print('to stderr', file=sys.stderr)"
r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
print(repr(r.stdout))
print(repr(r.stderr))