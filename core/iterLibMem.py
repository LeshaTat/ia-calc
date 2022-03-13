from functools import total_ordering
from .term import func, cortege, Var, Const, Func, pair, empty, genNewVar
from .notation import *
from .termAlgebra import listO, listApply, U, listIntersect, listPair, listApproxMinus

MemOperation = Func("MemOperation", 3)

def print_s(s):
  for it in s:
    print(str(it[0])+':'+str(it[1]))

def parse_s(s):
  return [(arg.args[0], arg.args[1]) for arg in s.args]

def make_stub(t, s, vs_all):
  return pair(
    t.clone(), 
    cortege(
      *[
        pair(
          genNewVar(vs_all, 'k'+str(i+1)), 
          genNewVar(vs_all, 'v'+str(i+1))
        ) for i, _ in enumerate(s)
      ]
    )
  )

def eval_mem_get(op):
  # MemOperation(t, s=((k_1, v_1),...,(k_n, v_n)), GetByAddr(k))
  t = op.args[0]
  s = parse_s(op.args[1])
  k = op.args[2]
  print_s(s)
  res = []
  vs_all = op.fillVars()
  print(make_stub(t, s, vs_all))
  for it in s:
    if it[0].s == k.s:
      break