from typing import NamedTuple
from functools import cached_property, total_ordering

def vN(n, s='v'):
  return Var(s+'_'+str(n))

def get(d, k, v):
    if k in d: return d[k]
    cv = v()
    d[k] = cv
    return cv

terms = {}

class VarGen:
  V = "abcdefghijklmnopqrstuvwxyz"
#    i = 0
  def __init__(self):
    self.i = 0
  def __call__(self):
    self.i += 1
    if self.i<=len(self.V): 
      return Var(self.V[self.i-1])
    return Var(self.V[len(self.V)-1]+str(self.i-len(self.V)+1))

class VarGenFromDict:
  V = "abcdefghijklmnopqrstuvwxyz"
  def __init__(self, d):
    self.d = d
    self.i = 0
  def __call__(self):
    v = genNewVar(self.d, self.V[self.i%len(self.V)])
    self.i = self.i + 1
    self.d[v] = 1
    return v


def norm_list(l, v=None, d=None):
  if d is None: d = {}
  if v is None: v = VarGen()
  return [norm(t, v, d) for t in l]

def norm(t, v=None, d=None):
  if v is None and d is None and t.isVar:
    return t
  if not isinstance(t, Term):
    raise ValueError(str(t)+" is not Term")
  if d is None: d = {}
  if v is None: v = VarGen()
  if t.isVar: return get(d, t.name, v)
  if t.isConst: return t
  return Func(t.name)(*[norm(tt, v, d) for tt in t.args])

def extract_vars(t1, t2, d=None):
  if not isinstance(t1, Term):
    raise ValueError(str(t1)+" is not Term")
  if not isinstance(t2, Term):
    raise ValueError(str(t2)+" is not Term")
  if d is None: d = {}
  if t1.isVar != t2.isVar or t1.isConst != t2.isConst or t1.name!=t2.name and not t1.isVar or len(t1.args)!=len(t2.args):
    raise ValueError("Terms "+str(t1)+" and "+str(t2)+" must have same structure")
  if t2.isVar:
    if t2.name not in d:
      d[t2.name] = t1
    elif d[t2.name] != t1:
      raise ValueError("Variable name "+str(t2)+" cannot have two values "+str(t1)+" and " +str(d[t2.name]))
    return d
  if t1.isConst: return d
  for i, _ in enumerate(t1.args):
    extract_vars(t1.args[i], t2.args[i], d)
  return d

@total_ordering
class Term:
  def __init__(self, name, isVar=False, args=(), isConst=False, s=""):
    self.name = name
    self.isVar = isVar
    self.args = args
    self.isConst = isConst
    self.s = s
  def clone(self):
    return Term(
      self.name, self.isVar,
      [arg.clone() for arg in self.args],
      self.isConst,
      self.s
    )
  def is_same(self, other):
    return self.isVar and other.isVar or self.norm == other.norm
  def isEmpty(self):
    return self.isConst and self.name=="empty"
  def __bool__(self):
    return not self.isEmpty()
  def __str__(self):
    return self.s
  def __le__(self, other):
    return self.s <= other.s
  def __eq__(self, other):
#    if self.norm.s==other.norm.s and self.s!=other.s:
#      print("Different "+str(self)+" "+str(other))
    return self.s==other.s
  def __hash__(self):
    return hash(self.s)
  @cached_property
  def groupID(self):
    if self.name=="ID":
      return self.args[0].s
    if not self.args:
      return ""
    listIDs = []
    for arg in self.args:
      argGroupID = arg.groupID
      if argGroupID:
        listIDs.append(argGroupID)
    return "("+",".join(listIDs)+")" if listIDs else ""
  @cached_property
  def norm(self):
    return norm(self)
  def has_other_vars(self, vs):
    if self.isVar:
      return self not in vs
    if self.isConst:
      return False
    return any(arg.has_other_vars(vs) for arg in self.args)
  def find_marks(self, marks, res=None):
    if res is None:
      res = {}
    if self.isConst and self.name in marks:
      res[self.name] = 1
    elif not self.isVar:
      for t in self.args:
        t.find_marks(marks, res)
    return res
  def fillVars(self, v=1, vs=None):
    if vs is None:
      vs = {}
    if self.isVar: 
      if self not in vs:
        if callable(v):
          vs[self] = v(self)
        else:
          vs[self] = v
      return vs
    if self.isConst: 
      return vs
    for arg in self.args:
      arg.fillVars(v, vs)
    return vs
  def genNewVar(self, s='v'):
    #TODO: cache fillVars 
    return genNewVar(self.fillVars(), s=s)
  def replace(self, addr, v):
    if not addr: 
      return v    
    if not self.args or addr[0] >= len(self.args):
      raise BaseException("Term replace failed")
    return gen_func_term(
      self.name, 
      [
        a.replace(addr[1:], v) if i==addr[0] else a for i, a in enumerate(self.args)
      ]
    )
    

def genNewVar(vs, s='v'):
  vInd = 1
  v = Var(s)
  while v in vs:
    v = vN(vInd, s=s)
    vInd+=1
  return v    


def Var(name: str):
  s = name
  return get(terms, s, lambda: Term(name, isVar=True, s=s))

def Const(name: str):
  s = '['+name+']'
  return get(terms, s, lambda: Term(name, isConst=True, s=s))

empty = Const("empty")

class FuncArgsInvalidCount(Exception):
  def __init__(self, name, des, cur):
    self.message = "Func "+name+" require "+str(des)+" args, but "+str(cur)+" specified."
  def __str__(self):
    return self.message

def gen_func_term(name, args):
  s = name+"("+", ".join([a.s for a in args])+")"
  return get(terms, s, lambda: Term(name=name, args=args, s=s))

class Func:
  name: str
  argCount: int
  def __init__(self, name: str, argCount: int=0):
    self.name = name
    self.argCount = argCount
  def __call__(self, *args):
    if self.argCount and len(args)!=self.argCount :
      raise FuncArgsInvalidCount(self.name, self.argCount, len(args))
    return gen_func_term(self.name, args)

def isFunc(t):
  return not t.isVar and not t.isConst and t.name=="" and len(t.args)==2
  
func = Func("", 2)
starVar = Var("*")
cortege = Func("")
pair = Func("", 2)
ID = Func("ID", 1)

def termToStr(term: Term):
  s = term.name
  if term.isVar:
    return 'Var("'+s+'")'
  if term.isConst:
    return 'Const("'+s+'")'
  return 'Func("'+s+'")'+"("+", ".join([termToStr(t) for t in term.args])+")"