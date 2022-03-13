from .term import get, empty, VarGen, Const, Func

class TermBox:
  def __init__(self, v):
    self.v = v
    self.n = None
  def termToNode(self, d):
    self.n = termToNode(self.v, d)
  def nodeToTerm(self, v):
    self.v = nodeToTerm(self.n, v)
    self.n = None
  def term(self):
    return self.v
  def clone(self):
    return TermBox(self.v)
  def isEmpty(self):
    return not self.v.isEmpty()
  def __str__(self):
    return self.v.s
  def __eq__(self, other):
    return self is other or self.v==other.v
  def __hash__(self):
    return hash(self.v)

class ErrorCycle(Exception):
    pass

class ErrorCycleFast(Exception):
    pass

class Node:
#    p = None;
#    v = None;
#    varname = None;
    def __init__(self, name: str, v=None, isConst=False):
      self.name=name
      self.v = v
      self.isConst = isConst
      self.isVar = v is None and not isConst
      self.p = None
      self.varname = None
      self.entered = False

def termToNode(t, d=None):
    if d is None: d = {}
    if t.isConst: return Node(t.name, isConst=True)
    if t.isVar: return get(d, t.name, lambda: Node(t.name))
    return Node(t.name, tuple([termToNode(tt, d) for tt in t.args]))

def find(n):
    nn = n
    while nn.p is not None and nn.p!=nn:
        nn = nn.p
    while n.p is not None and n.p!=nn:
        nnn = n
        n = n.p
        nnn.p = nn
    return nn

recurs = 0
def nodeToTerm(n, v=None):
    if v is None: v = VarGen()
    n = find(n)
    if n.entered: raise ErrorCycleFast
    if n.isConst: return Const(n.name)
    if n.v is None:
      if n.varname is None: n.varname=v()
      return n.varname
    global recurs
    recurs+=1
    if recurs>500:
        raise ErrorCycle
    n.entered = True
    res = tuple(nodeToTerm(nn, v) for nn in n.v)
    n.entered = False
    recurs-=1
    return Func(n.name)(*res)

def union(n1, n2):
    n = n1
    while n.p is not None:
        nn = n
        n = n.p
        nn.p = n2
    n.p = n2

def unifyNodes(n1, n2):
    n1 = find(n1)
    n2 = find(n2)
    if n1==n2: return True
    if n1.isVar and n2.isVar: 
        n1.p = n2
        return True
    if n1.isVar and not n2.isVar: 
        n1.p = n2
        return True
    if not n1.isVar and n2.isVar: 
        n2.p = n1
        return True
    if n1.name!=n2.name: return False
    if isinstance(n1.v, tuple) and isinstance(n2.v, tuple):
        n1.p = n2
        if len(n1.v)!=len(n2.v): return False
        for i in range(len(n1.v)):
            if not unifyNodes(n1.v[i], n2.v[i]): return False
    return True

def termPrecheck(t1, t2):
    if t1.isVar: return True
    if t2.isVar: return True
    if t1.name!=t2.name: return False
    if not t1.isConst and not t2.isConst:
        if len(t1.args)!=len(t2.args): return False
        for i in range(len(t1.args)):
            if not termPrecheck(t1.args[i], t2.args[i]): return False
        return True
    return True

def unify(t1, t2, extra1=None, extra2=None):
    if not termPrecheck(t1, t2): return empty
    d1 = {}
    n1 = termToNode(t1, d=d1)
    if extra1:
        for e in extra1:
            e.termToNode(d1)
    d2 = {}
    n2 = termToNode(t2, d=d2)
    if extra2:
        for e in extra2:
            e.termToNode(d2)
    if not unifyNodes(n1, n2): return empty
    try:
        v = VarGen()
        t = nodeToTerm(n1, v=v)
        if extra1:
            for e in extra1:
                e.nodeToTerm(v)
        if extra2:
            for e in extra2:
                e.nodeToTerm(v)
        return t
    except ErrorCycle:
        print("Cycle error")
        print(t1)
        print(t2)
        return empty
    except ErrorCycleFast:
        return empty
    
    