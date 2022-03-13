from functools import total_ordering
from sortedcontainers import SortedList
from .term import func, cortege, Var, Const, Func, pair, empty
from .notation import *
from .termAlgebra import listO, listApply, U, listIntersect, listPair, listApproxMinus

x = Var('x')
y = Var('y')
q = Var('q')

@total_ordering
class MapItem:
  def __init__(self, m = None):
    if m is None: m = {}
    self.m = m
    self.s = ''
    self.s = ";".join([str(k)+':'+str(self.m[k]) for k in sorted(self.m)])
    if self.s=="": self.s = "0"
#    for k in sorted(self.m):
#      self.s += str(k)+':'+str(self.m[k])+';'
  def put(self, k, v):
    r = {**self.m}
    r[str(k)] = v
    if v == c0: del r[k]
    return MapItem(r)
  def get(self, k):
    s = str(k)
    if s in self.m: return self.m[s]
    return c0
  def __str__(self):
    return self.s
  def __lt__(self, other):
    return self.s <= other.s
  def __eq__(self, other):
    return self.s==other.s

class MapList:
  def __init__(self, l = None):
    if l is None: l = [MapItem()]
    self.l = l    
  def isIn(self, other):
    k = 0
    other_len = len(other.l)
    for item in self.l:
      found = False
      while k < other_len and not found:
        if other.l[k] == item: found = True
        k = k + 1
      if not found: return False
    return True     
  def add(self, item):
    if item in self.l:
      return self
    l = self.l.copy()
    l.append(item)
    l.sort()
    return MapList(l)
  def __str__(self):
    return ", ".join([str(it) for it in self.l])

class MapModel:
  def __init__(self, t = None, default = None, cursor = None, identifier = 0):
    if default is None: default = MapList()
    if cursor is None: cursor = MapItem()
    if t is None: t = empty
    self.t = t
    self.default = default
    self.cursor = cursor
    self.identifier = identifier
    self.fApplied = None

  def get(self, addr):
    if str(addr) == str(self.addr()): return [self]
    default = self.default.add(self.cursor)
    t = MapModel.extendTerm(self.term(), addr)
    return [MapModel(t, default, item, self.identifier) for item in self.default.l]
  
  def put(self, k, addr, v):
    if str(addr) == str(self.addr()):
      cursor = self.cursor.put(k, v)
      return [MapModel(self.t, self.default, cursor, self.identifier)]
    t = MapModel.extendTerm(self.term(), addr)
    default = self.default.add(self.cursor)
    return [MapModel(t, default, item.put(k, v), self.identifier) for item in self.default.l]

  def term(self):
    return self.t.args[0]
  
  def addr(self):
    return self.t.args[1]

  @staticmethod
  def extendTerm(t, addr):
    return pair(t, addr)

  @staticmethod
  def extendFunc(f):
    if isinstance(f, list):
      return [MapModel.extendFunc(c) for c in f]
    return func(func(x, y), func(MapModel.extendTerm(x, q), MapModel.extendTerm(y, q)))(f)

  def applyList(self, l):
    nxt = []
    for fOne in l: self.applyTerm(fOne).appendToList(nxt)
    return nxt

  def applyTerm(self, f, save_f_applied=False):
    t = f(self.t)
    if t.isEmpty(): return MapModel(empty)

    nxt = MapModel(t, self.default, self.cursor, self.identifier)
    nxt.fApplied = f
    if save_f_applied:
      nxt.fApplied = self.fApplied
#    for ckv in self.m:
#      nckv = f(self.termed(ckv))
#      if nckv.isEmpty(): continue
#      nxt.add(nckv)
    return nxt

  def appendToList(self, l):
    if self.t.isEmpty() or self.isIn(l):
      return l
    l.append(self)
    return l

  def isInOne(self, other):
    if self == other: return True
    if self.cursor != other.cursor: return False
    if str(self.t) != str(other.t): return False
#    if not self.t.isIn(other.t): return False
    return self.default.isIn(other.default)

  def isIn(self, other):
    if isinstance(other, list):
      for m in other:
        if self.isInOne(m): return True
      return False
    return self.isInOne(other)


class IterMap2:
  def __init__(self, t, m = None):
    if m is None: m = []
    self.t = t
    self.m = m

  def clone(self):
    other = IterMap2(self.t)
    other.m = [*self.m]
    return other

  def termed(self, t):
    return pair(self.t, t)

  def add(self, kv):
    k = kv.args[0]
    i = len(self.m)-1
    while i>=0:
      if self.termed(self.m[i].args[0]).isIn(self.termed(k)):
        self.m.pop(i);
      elif self.termed(kv).isIn(self.termed(self.m[i])):
        return self
      i = i-1
    self.m.append(kv)
    return self

  def get(self, k):
    lst = []
    tk = self.termed(k)
    for ckv in reversed(self.m):
      ck = ckv.args[0]
      cv = ckv.args[1]
      r = func(self.termed(ck), self.termed(cv))(tk)
      if not r.isEmpty():
        lst.append(r)
        if tk.isIn(self.termed(ck)): return lst      
    return lst

  @staticmethod
  def extendFunc(f):
    if isinstance(f, list):
      return [IterMap2.extendFunc(c) for c in f]
    return func(func(x, y), func(pair(x, q), pair(y, q)))(f)

  def applyList(self, l):
    nxt = []
    for fOne in l: self.applyTerm(fOne).appendToList(nxt)
    return nxt

  def applyTerm(self, f):
    t = f(self.termed(self.t.genNewVar('x')))
    if t.isEmpty(): return IterMap2(empty)

    nxt = IterMap2(t.args[0])
#    for ckv in self.m:
#      nckv = f(self.termed(ckv))
#      if nckv.isEmpty(): continue
#      nxt.add(nckv)
    return nxt

  def isIn(self, other):
    if isinstance(other, list):
      for m in other:
        if self.isIn(m): return True
      return False
    return self.t.isIn(other.t)

  def isInM(self, other):
    for kv in reversed(self.m):
      was = False
      for okv in reversed(other.m):
        ok = okv.args[0]
        if self.termed(kv).isIn(other.termed(okv)):
          was = True
          break
        ikv = self.termed(kv).unify(other.termed(func(ok, Var('*'))))
        if ikv.isEmpty(): continue
        if not ikv.isIn(other.termed(okv)): return False          
      if not was: return False
    return True
  
  def termedList(self):
    return [self.termed(v) for v in self.m]

  def appendToList(self, l):
    if self.t.isEmpty() or self.isIn(l):
      return l
    l.append(self)
    return l
    



