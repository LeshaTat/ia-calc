from .term import func, cortege, Var, Const, Func, pair
from .notation import *
from .termAlgebra import listO, listApply, U, listIntersect, listPair, listApproxMinus, termO
import itertools

s = Var('s')
q = Var('q')
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

def printl(l):
  print('[')
  for t in l:
    print(str(t.args[0])+' ->\n'+str(t.args[1])+'\n')
#    print(str(t.args[0].groupID)+' ->\n'+str(t.args[1].groupID)+'\n')
  print(']')


def breadth_first_search(f, cbk, s0=None, include_all=False):
  if s0 is None: s0 = c0
  nxt = [(func(StateMesIn(s0, x), StateMesIn(s0, x)), [])]
  used = []
  while nxt:
    cur = nxt
    nxt = []
    for (cX, h) in cur:
      cNext = listO(f, [cX])
      for pair in cNext:
        n = pair.args[1]
        preN = pair.args[0]
        nPair = pair
        hNext = h
        if pair.isIn(used): continue
        if n.isIn(StateMesOut(s, x)):
          if not cbk(nPair, h):
            continue
#          hNext = hNext + [func(preN, n)]   
          nX = func(StateMesOut(s, x), StateMesIn(s, y))(n)
          nPair = func(nX, nX)
        else:
          if include_all:
            cbk(nPair, h)
          nX = n
        pair.appendToList(used)
        nxt.append((nPair, hNext))

def isFIn(t1, t2):
  return t1.args[0].groupID==t2.args[0].groupID and t1.args[0].isIn(t2.args[0])

def appendPair(pair, nn):
  n = nn.get(pair.args[0].groupID, [])
  n = [el for el in n if not isFIn(el, pair)]
  if not any(isFIn(pair, el) for el in n):
    n.append(pair)
  else:
    return False
  nn[pair.args[0].groupID] = n
  return True

def tighten(f, s0=None, include_all=False):
  nn = {}
  breadth_first_search(f, lambda pair, h: appendPair(pair, nn), s0=s0, include_all=include_all)
  n = []
  for _, value in nn.items():
#    print('Len:'+str(len(value)))
    n = n + value
#  print('----')
  return n

def tighten_iter(f):
  return tighten(f)
  iterPattern = func(Iter(x), y)
  iterF = [it for it in f if it.isIn(iterPattern)]
  iterOutPattern = func(x, Iter(y))
  last = len(iterF)
  added = [(it, last) for it in f if it.isIn(iterOutPattern)]
#  checkedFrom = {}
  j = 0
  statePattern = func(StateMes(s, x), StateMes(d, y))  
  res = [cur for cur in f if cur.isIn(statePattern)]
  while added:
    added_next = []
    for a, fa in added:
      iterCurList = [(a, fa, True)]
#      checkedFrom[a] = 0
      for i, fCur in enumerate(iterF):
        iterNextList = []
        for iterCur, fr, old in iterCurList:
          nextCur = fCur.o(iterCur)
          if nextCur:
#              iterNextList.append((nextCur, checkedFrom.get(nextCur, None)))
            iterNextList.append((nextCur, i+1, False))
#              checkedFrom[nextCur] = i+1
          if not old or fr>i+1:
            iterNextList.append((iterCur, fr, old))
        iterCurList = iterNextList
      for iterCur, fr, old in iterCurList:
        if iterCur.isIn(statePattern):
          res.append(iterCur)
        elif not old:
          added_next.append((iterCur, fr))
      
    added = added_next
    j = j+1
    print(str(j)+':'+str(len(added_next)))
  print('res:'+str(len(res)))
  return res

def tighten_iter_2(f):
  statePattern = func(StateMes(s, x), StateMes(d, y))  
  iterOutPattern = func(x, Iter(y))
  iterPattern = func(Iter(x), y)
  iterF = [it for it in f if it.isIn(iterPattern)]
#  iterOutPattern = func(x, Iter(y))
  added = [it for it in f if it.isIn(iterOutPattern)]
  res = [cur for cur in f if cur.isIn(statePattern)]
  grouped = {}
  for curIter in iterF:
    group = grouped.get(curIter.args[0].groupID, [])
    group.append(curIter)
    grouped[curIter.args[0].groupID] = group
  j = 0
  while added:
    added_next = []
    for item in added:
      for curIter in grouped.get(item.args[1].groupID, []):
        nextItem = curIter.o(item)
        if nextItem:
          if nextItem.isIn(iterOutPattern):
            added_next.append(nextItem)
          else:
            res.append(nextItem)
    added = added_next
    j = j+1
    print(str(j)+':'+str(len(added_next)))
  print('res:'+str(len(res)))
  return res

