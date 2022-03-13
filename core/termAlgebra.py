from .term import get, func, empty, starVar, Var, isFunc, Term
from .unify import unify as unifyTerms, VarGen, termPrecheck, termToNode, nodeToTerm, unifyNodes, Node, ErrorCycle
from .notation import pair
from functools import cache

vA = Var('a')
vB = Var('b')

def printl(l):
  print('[')
  for t in l:
    print(str(t))
  print(']')

@cache
def termTermApply(t1, t2, extra=None):
  if t1==empty or t2==empty: return empty
  t = unify(t1, func(t2, starVar), extra2=extra)
  if t==empty: return empty
  if t.isVar: return Var('a')
  return t.args[1]

@cache
def unify(t1, t2, extra1=None, extra2=None):
  if t1.norm.s==t2.norm.s: return t1.norm if not extra1 else t1
  if t1.norm.s>t2.norm.s: return unify(t2, t1, extra2=extra1, extra1=extra2)
  return unifyTerms(t1, t2, extra1=extra1, extra2=extra2)

#@cache
def termTermO(t1, t2):
  if t1.isVar: 
    t1 = func(vA, vB)
  elif not isFunc(t1):
    return empty

  if t2.isVar:
    t2 = func(vA, vB)
  elif not isFunc(t2):
    return empty

  if not termPrecheck( t2.args[1], t1.args[0] ): return empty
  n1 = termToNode(t1)
  n2 = termToNode(t2)
  if not unifyNodes(n2.v[1], n1.v[0]): return empty
  try:
    return nodeToTerm( Node("", (n2.v[0], n1.v[1])) )
  except ErrorCycle:
    return empty

def termListO(t, l):
  n = []
  for t1 in l:
    if not isinstance(t1, Term):
      printl(l)
    t2 = termTermO(t, t1)
    if t2==empty: continue
    if t2 in n: continue
    n.append(t2)
  return n

def termO(t, l):
  if isinstance(l, list): return termListO(t, l)
  return termTermO(t, l)

def termListApply(t, l):
  n = []
  for t1 in l:
    if not isinstance(t1, Term):
      printl(l)
    t2 = termTermApply(t, t1)
    if t2==empty: continue
    if t2 in n: continue
    n.append(t2)
  return n

def termApply(t, l):  
  if isinstance(l, list): return termListApply(t, l)
  if t.isConst and not t.isEmpty():
    raise BaseException("Applying const term possibly erroneous " + str(t))
  return termTermApply(t, l)

def termApplyGently(t, l):
  res = termApply(t, l)
  return res if res else l

Term.__call__ = termApply
Term.apply = termApply
Term.applyGently = termApplyGently
Term.unify = unify
Term.o = termO

def termInTerm(t1, t2):
  return t1.unify(t2).norm==t1.norm

def termInList(t, l):
  for t1 in l:
    if termInTerm(t, t1): 
      return True
  return False

def termIn(t, l):
  if isinstance(l, list): return termInList(t, l)
  return termInTerm(t, l)


Term.isIn = termIn
    
def termListAppend(t2, l, **kwargs):
  if t2==empty or t2.isIn(l):
    return l
  if "copy" in kwargs: 
    lc = l.copy()
    lc.append(t2)
    return lc
  else:
    l.append(t2)
    return l
Term.appendToList = termListAppend
    
def termIntersect(t, l):
  n = []
  for t1 in l:
    t2 = unify(t, t1)
    if t2!=empty: n.append(t2)
  return n

Term.intersect = termIntersect
    
def listIntersect(l1, l2):
  n = []
  for t in l2:
    n.extend(t.intersect(l1))
  return n    

def UInc(l1, l2):
  lInc = []
  for t in l2:
    if not t.isIn(l1):
      lInc.append(t)
  return (l1+lInc, lInc)

def U(l1, l2):
  return UInc(l1, l2)[0]

def termListApplyBy(t, l, result=None):
  if result is None: result = []
  for tl in l:
    tl.apply(t).appendToList(result)
  return result

def listApply(l1, l2):
  n = []
  for t2 in l2:
    termListApplyBy(t2, l1, n)
  return n

Term.applyBy = termListApplyBy

def listSimplify(l):
  n = []
  while len(l):
    t = l[len(l)-1]
    l = [ t1 for t1 in l if not t1.isIn(t) ]
    n = [ t1 for t1 in n if not t1.isIn(t) ]
    n.append(t)
  return n

def listApproxMinus(l1, l2):
  n = []
  for t1 in l1:
    if next((t2 for t2 in l2 if t1.isIn(t2)), empty)==empty:
      n.append(t1)
#  for t2 in l2:
#    if next((t1 for t1 in l1 if t2.isIn(t1)), empty)==empty:
#      n.append(t2)
  return n

def listO(l1, l2):
  n = []
  for t11 in l1:
    for t12 in l2:
      t2 = t11.o(t12)
      if t2!=empty: n.append(t2)
  return n

def termPairNoCommonVars(t1, t2):
  n1 = termToNode(t1)
  n2 = termToNode(t2)
  v = VarGen()
  return pair(nodeToTerm(n1, v), nodeToTerm(n2, v))

def listPair(l1, l2):
  return [termPairNoCommonVars(t1, t2) for t1 in l1 for t2 in l2]
