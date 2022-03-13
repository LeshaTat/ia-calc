from functools import cached_property
from .term import func, cortege, Var, Const, Func
from .notation import *
from .termAlgebra import listO, listApply, U, listIntersect, listPair, listApproxMinus
from .iter import tighten, tighten_iter

x = Var('x')
y = Var('y')
z = Var('z')
a = Var('a')
s = Var('s')
d = Var('d')
q = Var('q')
s0 = Var('s0')
k = Var('k')

StateMesIn = Func("StateMesIn", 2)
StateMesOut = Func("StateMesOut", 2)

upRemap1 = [
  func(
    func(StateMes(s, x), StateMes(d, y)),
    func(StateMes(UpState(s, q), x), StateMes(UpState(d, q), y))
  ),
  func(
    func(StateMes(s, x), Iter(y)),
    func(StateMes(UpState(s, q), x), Iter(IterUp(y, q)))
  ),
  func(
    func(Iter(x), Iter(y)),
    func(Iter(IterUp(x, q)), Iter(IterUp(y, q)))
  ),
  func(
    func(Iter(x), StateMes(d, y)),
    func(Iter(IterUp(x, q)), StateMes(UpState(d, q), y))
  )
]

upRemap2 = [
  func(
    func(x, StateMes(UpState(s, q), OutMes(UpMes(a)))),
    func(x, StateMes(UpState(s, q), OutMes(a)))
  ),
  func(
    func(x, StateMes(UpState(s, q), OutMes(DownMes(a)))),
    func(x, Iter(IterDown(s, StateMesIn(q, OutMes(a)))))
  ),
  func(
    func(x, StateMes(UpState(s, q), CallMes(k, a))),
    func(x, StateMes(UpState(s, q), CallMes(k, a)))
  ),
  func(
    func(x, Iter(y)),
    func(x, Iter(y))
  )
]

upRemap3 = [
  func(
    func(StateMes(UpState(s, q), OutMes(UpMes(a))), y),
    func(StateMes(UpState(s, q), OutMes(a)), y)
  ),
  func(
    func(StateMes(UpState(s, q), OutMes(DownMes(a))), y),
    func(Iter(IterDown(s, StateMesOut(q, OutMes(a)))), y)
  ),
  func(
    func(StateMes(UpState(s, q), CallMes(k, a)), y),
    func(StateMes(UpState(s, q), CallMes(k, a)), y)
  ),
  func(
    func(Iter(x), y),
    func(Iter(x), y)
  )
]

downRemap1 = [
  func(
    func(StateMes(s, x), StateMes(d, y)),
    func(Iter(IterDown(q, StateMesIn(s, x))), Iter(IterDown(q, StateMesOut(d, y))))
  ),
  func(
    func(Iter(x), StateMes(d, y)),
    func(Iter(IterDown(q, Iter(x))), Iter(IterDown(q, StateMesOut(d, y))))
  ),
  func(
    func(StateMes(s, x), Iter(y)),
    func(Iter(IterDown(q, StateMesIn(s, x))), Iter(IterDown(q, Iter(y))))
  ),
  func(
    func(Iter(x), Iter(y)),
    func(Iter(IterDown(q, Iter(x))), Iter(IterDown(q, Iter(y))))
  ),
]

downRemap2 = [
  func(
    func(x, Iter(IterDown(q, StateMesOut(s, CallMes(k, a))))),
    func(x, StateMes(DownCallState(q, s), CallMes(k, a)))
  ),
  func(
    func(x, Iter(IterDown(q, StateMesOut(s, OutMes(y))))),
    func(x, Iter(IterDown(q, StateMesOut(s, OutMes(y)))))
  ),
  func(
    func(x, Iter(IterDown(q, Iter(y)))),
    func(x, Iter(IterDown(q, Iter(y))))
  )
]

downRemap3 = [
  func(
    func(Iter(IterDown(q, StateMesIn(s, CallMes(k, a)))), y),
    func(StateMes(DownCallState(q, s), CallMes(k, a)), y)
  ),
  func(
    func(Iter(IterDown(q, StateMesIn(s, OutMes(x)))), y),
    func(Iter(IterDown(q, StateMesIn(s, OutMes(x)))), y)
  ),
  func(
    func(Iter(IterDown(q, Iter(x))), y),
    func(Iter(IterDown(q, Iter(x))), y)
  )
]
def printl(l):
  print('[')
  for t in l:
    print(str(t.args[0])+' -> \n'+str(t.args[1])+"\n")
  print(']')

def replaceMem(t, k):
  if t.isIn(func(z, StateMes(s, CallMes(Mem(a), x)))):
    t = func(
      func(z, StateMes(s, CallMes(Mem(a), x))),
      func(z, StateMes(s, CallMes(Mem(pair(k, a)), x)))
    )(t)
  if t.isIn(func(StateMes(s, CallMes(Mem(a), x)), z)):
    t = func(
      func(StateMes(s, CallMes(Mem(a), x)), z),
      func(StateMes(s, CallMes(Mem(pair(k, a)), x)), z)
    )(t)
  return t

def comp(f, g):
#  g1 = listApply(downRemap1, g)
#  g2 = listApply(downRemap2, g1)
#  g3 = listApply(downRemap3, g2)
#  printl(g)
#  printl(g1)
#  printl(g2)
#  printl(g3)
  f = [replaceMem(t, c0) for t in f]
  g = [replaceMem(t, c1) for t in g]
  up = listApply(upRemap3, listApply(upRemap2, listApply(upRemap1, f)))
  upC0 = func(
    func(StateMes(UpState(c0, c0), x), y), 
    func(StateMes(c0, x), y)
  )(up)  
  down = listApply(downRemap3, listApply(downRemap2, listApply(downRemap1, g)))
  return U(
    U(up, upC0),
    down
  )

VarState = Func("VarState", 1)

def iter_var(var_name):
  var = Const("var_"+var_name)
#  return IterItem([
#    func(StateMes(c0, OutMes(x)), StateMes(c1, CallMes(var, StateMes(c0, OutMes(x))))),
#    func(StateMes(c1, CallMes(var, StateMes(c0, OutMes(x)))), StateMes(c0, OutMes(x))),
#  ])
#  return IterItem([
#    func(StateMes(s, OutMes(x)), StateMes(s, CallMes(var, StateMes(s, OutMes(x))))),
#    func(StateMes(s, CallMes(var, StateMes(d, OutMes(x)))), StateMes(d, OutMes(x))),
#  ])
  return IterItem([
    func(StateMes(c0, OutMes(x)), StateMes(c1, CallMes(var, StateMes(c0, OutMes(x))))),
    func(StateMes(VarState(s), OutMes(x)), StateMes(c1, CallMes(var, StateMes(s, OutMes(x))))),
    func(StateMes(c1, CallMes(var, StateMes(d, OutMes(x)))), StateMes(VarState(d), OutMes(x))),
  ])

class IterItem(list):
  def __call__(self, *args, no_tighten=False):
    if len(args)==1:
      res = comp(self, args[0])
      if not no_tighten:
        res = tighten_iter(res)
      return IterItem(res)
    if len(args)>1:
      res = self(args[0], no_tighten=no_tighten)(*args[1:], no_tighten=no_tighten)      
#      res = self(args[0])(*args[1:])
      if not no_tighten:
        res = res.tighten()
      return res
    return self
  def tighten(self):  
    return IterItem(tighten_iter(self))
