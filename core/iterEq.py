from .term import func, cortege, Var, Const, Func
from .notation import *
from .termAlgebra import listO, listApply, U, listIntersect, listPair, listApproxMinus
from .iter import breadth_first_search, tighten

s = Var('s')
sf = Var('sf')
sg = Var('sg')
d = Var('d')
df = Var('df')
dg = Var('dg')
z = Var('z')
sn = Var('sn')
dn = Var('dn')
x = Var('x')
y = Var('y')
xg = Var('xg')
yg = Var('yg')
xf = Var('xf')
yf = Var('yf')
a = Var('a')
b = Var('b')

def automaton_pair_tighten(f_tighten, g_tighten):
  return tighten(listApply([func(
      pair(
        func(StateMes(s, x), StateMes(sn, a)),
        func(StateMes(d, x), StateMes(dn, b))
      ),
      func(
        StateMes(pair(s, d), x),
        StateMes(pair(sn, dn), pair(a, b))
      )
    )], 
    listPair(f_tighten, g_tighten)
  ), s0=pair(c0, c0))

def automaton_dom_states(f):
  return func(
    func(
      StateMes(s, x),
      StateMes(d, y)
    ),
    s
  )(f)

def automaton_dom_mes(sf, f):
  sfx = sf.genNewVar('x')
  return func(
    func(
      StateMes(sf, sfx),
      StateMes(sf.genNewVar('d'), sf.genNewVar('y'))
    ),
    sfx
  )(f)

def automaton_diff_state(sfg, fg, f, g):
  print("Diff state " +str(sfg))
  sf = sfg.args[0]
  sg = sfg.args[1]
  fgDom = automaton_dom_mes(sfg, fg)
  fDom = automaton_dom_mes(sf, f)
  gDom = automaton_dom_mes(sg, g)
  printl(fDom)
  printl(gDom)
  fMinus = listApproxMinus(fDom, fgDom)
  gMinus = listApproxMinus(gDom, fgDom)
  return (U(
    fMinus,
    gMinus
  ), fDom, gDom, fgDom)

def automaton_diff(f, g):
  f_tighten = tighten(f)
  g_tighten = tighten(g)
  fg_tighten = automaton_pair_tighten(f_tighten, g_tighten)
  res = []
  func_diff = listApproxMinus(fg_tighten, [func(
    StateMes(s, x),
    StateMes(d, pair(y, y))
  )])
  f_dom = func(
    func(x, y), x
  )(f_tighten)
  g_dom = func(
    func(x, y), x
  )(g_tighten)
  fg_dom = func(
    func(x, y), x
  )(fg_tighten)
  f_from_fg_dom = func(StateMes(pair(s, d), x), StateMes(s, x))(fg_dom)
  g_from_fg_dom = func(StateMes(pair(s, d), x), StateMes(d, x))(fg_dom)
  f_diff = listApproxMinus(f_dom, f_from_fg_dom)
  g_diff = listApproxMinus(g_dom, g_from_fg_dom)
  return (func_diff, f_diff, g_diff)

def printl(l):
  print('[')
  for t in l:
    print(str(t))
  print(']')

def print_diff(diff):
  (func_diff, f_diff, g_diff) = diff
  if not func_diff and not f_diff and not g_diff: 
    print('No diff')
    return
  if func_diff:
    print('Func diff')
    printl(func_diff)
  if f_diff:
    print("Dom deficiency (2 < 1)")
    printl(f_diff)
  if g_diff:
    print("Dom deficiency (1 < 2)")
    printl(g_diff)

def backtrace_check(pair, h):
  ret = pair.args[1]
  retMes = ret.args[1]
  if retMes.args[0] != retMes.args[1]:
    print("Diff in "+str(retMes))
    for t in h:
      t_fr = t.args[0]
      t_to = t.args[1]
      print(str(t_fr.args[1])+' - '+str(t_to.args[1].args[0]))
    printl(h)

def backtrace_func_diff(f, g):
  f_tighten = f.tighten()
  g_tighten = g.tighten()
  breadth_first_search(listApply([func(
      pair(
        func(StateMes(s, x), StateMes(sn, a)),
        func(StateMes(d, x), StateMes(dn, b))
      ),
      func(
        StateMes(pair(s, d), x),
        StateMes(pair(sn, dn), pair(a, b))
      )
    )], 
    listPair(f_tighten, g_tighten)
  ), backtrace_check, s0=pair(c0, c0))
