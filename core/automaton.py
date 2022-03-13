from copy import deepcopy
from .term import func, cortege, Var, Const, Func
from .notation import *
from .termAlgebra import listO, listApply, U, listIntersect, listPair, listApproxMinus
from .iterRule import IterVarNode, IterFuncNode, IterRuleNode
from .operator import Operator, var as opVar, const as opConst

s = Var('s')
d = Var('d')
z = Var('z')
sn = Var('sn')
dn = Var('dn')
x = Var('x')
y = Var('y')
a = Var('a')
b = Var('b')

def cartesian(cf, cg):
  (cf0, f) = cf
  (cg0, g) = cg
  return (pair(cf0, cg0), listApply([func(
      pair(
        func(StateMes(s, x), StateMes(sn, a)),
        func(StateMes(d, x), StateMes(dn, b))
      ),
      func(
        StateMes(pair(s, d), x),
        StateMes(pair(sn, dn), pair(a, b))
      )
    )], 
    listPair(f, g)
  ))

def fullADesc(cf):
  (cInit, f) = cf
  h = opVar()
  def ims(xOp):
    return xOp.apply(func(
      func(a, StateMes(s, x)),
      func(StateMes(s, y), StateMes(s, y))
    ), True)
  op = h.set( opConst(f).o( h.U( ims(h) ).U([
    func(
      StateMes(cInit, x),
      StateMes(cInit, x)
    )
  ])) )
  #op = h.set( c(f).o( h.U(["0 0 ; x -> 0 0 ; x"])) )
  res = op.calcFull()
  return (cInit, res)

def aStates(af):
  return func(
    func(
      StateMes(s, x),
      StateMes(d, y)
    ),
    s
  )(af[1])

def aDom(sf, af):
  sfx = sf.genNewVar('x')
  return func(
    func(
      StateMes(sf, sfx),
      StateMes(sf.genNewVar('z'), sf.genNewVar('y'))
    ),
    sfx
  )(af[1])

def aDiffState(sfg, afg, af, ag): 
  sf = func(pair(s, d), s)(sfg)
  sg = func(pair(s, d), d)(sfg)
  fgDom = aDom(sfg, afg)
  fDom = aDom(sf, af)
  gDom = aDom(sg, ag)
  fMinus = listApproxMinus(fDom, fgDom)
  gMinus = listApproxMinus(gDom, fgDom)
  return (U(
    fMinus,
    gMinus
  ), fDom, gDom, fgDom)

def aDiff(af, ag):
  desc = fullADesc(cartesian(af, ag))
  aff = fullADesc(af)
  agf = fullADesc(ag)
  res = []
  r = listApproxMinus(desc[1], [func(
    StateMes(s, x),
    StateMes(d, pair(y, y))
  )])
  states = aStates(desc)
  if r: res.append(r)
  for sfg in states:
    ds, fm, gm, fgm = aDiffState(sfg, desc, aff, agf)
    if ds: res.append((sfg, ds, fm, gm, fgm))

  return res

def printl(l):
  print('[')
  for t in l:
    print(str(t))
  print(']')

def printDiff(diff):
  if len(diff)==0: 
    print('No diff')
    return
  for d in diff:
    if isinstance(d, tuple):
      print('State diff: '+str(d[0]))
      printl(d[1])
      printl(d[2])
      printl(d[3])
      printl(d[4])
      continue
    print('Func diff')
    printl(d)