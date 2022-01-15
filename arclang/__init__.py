import sys
import json
from contextlib import contextmanager

def alist(x):
  return isinstance(x, (tuple, list))

def anumber(x):
  return isinstance(x, (int, float))

def nil(x):
  return x is None

def none(x):
  return len(x) <= 0

def some(x):
  return len(x) >= 1

def hd(x):
  if some(x):
    return x[0]

def tl(x):
  return x[1:]

def carif(x):
  if alist(x):
    return hd(x)
  else:
    return x

def add(l, x):
  l.append(x)

def drop(l):
  return l.pop()

def map(f, l):
  return [f(x) for x in l]

def stringify(x):
  return str(x)

def concat(xs, sep=""):
  return sep.join(xs)

def flat(x, *, out=None):
  if out is None:
    out = []
  if alist(x):
    for v in x:
      flat(v, out=out)
  else:
    out.append(x)
  return out

buffer_stack = []

def current_buffer():
  if buffer_stack:
    return buffer_stack[-1]

def write(s):
  sys.stdout.write(s)

def tos(*args):
  return concat(map(stringify, args))

def insert(*x):
  if nil(current_buffer()):
    write(tos(*x))
    return x
  else:
    for v in x:
      if not nil(v):
        add(current_buffer(), v)

def pr(x, *args):
  for v in [x, *args]:
    insert(v)
  if nil(current_buffer()):
    return x

def prn(x, *args):
  v = pr(x, *args)
  pr("\n")
  return v

@contextmanager
def tolist(buffer_factory=list):
  buffer = buffer_factory()
  add(buffer_stack, buffer)
  try:
    yield buffer
  finally:
    drop(buffer_stack)

@contextmanager
def prlist(buffer_factory=list):
  with tolist(buffer_factory=buffer_factory) as buffer:
    yield buffer
  if not nil(current_buffer()):
    add(current_buffer(), buffer)
  # pr(buffer)

@contextmanager
def tostring(buffer_factory=list):
  with tolist(buffer_factory=buffer_factory) as buffer:
    def value():
      return concat(map(stringify, flat(buffer)))
    yield value

def pair(l):
  r = []
  n = len(l)
  for i in range(0, n, 2):
    x = l[i]
    y = l[i + 1] if i + 1 < n else None
    r.append((x, y))
  return r

@contextmanager
def tag(name, **props):
  with prlist() as buffer:
    with prlist():
      pr("jsx")
      pr(name)
      if props:
        pr(props)
    yield buffer

def center():
  return tag("center")

def underline():
  return tag("u")

def tab():
  return tag("table", border=0)

def tr():
  return tag("tr")

def td():
  return tag("td")

@contextmanager
def trtd():
  with tr() as row:
    with td():
      yield row

def tdr():
  return tag("td", align="right")

def prrow(*args):
  with tr() as out:
    for a in args:
      with (tdr if anumber(a) else td)():
        pr(a)
    return out

def prbold(*args):
  with tag("b") as out:
    pr(*args)
    return out

def para(*args):
  with tag("p") as out:
    if args:
      pr(*args)
    return out

def escape(x):
  return json.dumps(x)

@contextmanager
def whitepage():
  with tag('html') as out:
    with tag("body", bgcolor="white", alink="blue"):
      yield out

def html(*args, indent=0):
  with tostring() as out:
    for node in args:
      if carif(carif(node)) == "jsx":
        jsx, name, *props = hd(node)
        props = props[0] if props else {}
        assert jsx == "jsx"
        opts = ' '.join([f'{k}={escape(v)}' for k, v in props.items()])
        if opts:
          opts = ' ' + opts
        pr("  " * indent)
        pr("<")
        pr(name)
        pr(opts)
        prn(">")
        pr(html(*tl(node), indent=indent + 1))
        pr("  " * indent)
        pr("</")
        pr(name)
        prn(">")
      else:
        pr("  " * indent)
        prn(node)
    return out()

