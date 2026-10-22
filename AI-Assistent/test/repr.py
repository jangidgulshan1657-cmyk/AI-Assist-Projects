s = "hello\n"
print(s)         # hello  (plus an invisible newline, so you can't see it)
print(repr(s))   # 'hello\n'

r = "to stdout\n"
print(r)
print(repr(r))
print(repr(r.strip()))