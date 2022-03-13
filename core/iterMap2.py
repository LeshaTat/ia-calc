from functools import cached_property
from collections import deque
from functools import total_ordering
from .unify import TermBox, termPrecheck
from sortedcontainers import SortedList
from .term import VarGenFromDict, extract_vars, func, cortege, Var, Const, Func, norm_list, pair, empty
from .notation import *
from .termAlgebra import listO, listApply, U, listIntersect, listPair, listApproxMinus, termTermApply

x = Var('x')
y = Var('y')
q = Var('q')

class FrameExtractor:
  def __init__(self):
    self.ind = 0
    self.v = {}
    self.vars = []
    self.varsInds = {}
    self.frame = []
  def extractVars(self, t):
    vs = {}
    t.fillVars(vs=vs)
    self.vars = tuple(sorted([k.name for k in vs]))
    for i, k in enumerate(self.vars):
      self.varsInds[k] = i
  def getVars(self):
    return self.vars
  def makeFrame(self, t):
    if t.isVar:
      return cN(self.varsInds[t.name])
    if t.isConst:
      return Const(t.s)
    return Func(t.name)(*[self.makeFrame(arg) for arg in t.args])

def extractFrame(t):
  extractor = FrameExtractor()
  extractor.extractVars(t)
  return (extractor.getVars(), extractor.makeFrame(t))

class MapRecord:
  def __init__(self, k, v):
    self.k = k
    self.v = v
  def precheck(self, k):
    return termPrecheck(k, self.k)
  def keyIsEq(self, other):
    return self.k.s == other.k.s
  def box(self, l):
    l.append(TermBox(self.k))
    l.append(TermBox(self.v))
  def unbox(self, l):
    self.v = l.pop()
    self.k = l.pop()

def vars_to_id(t):
  vs = t.fillVars()
  return (len(vs), ",".join(sorted(v.name for v in vs)))

class Partition:
  def __init__(self, lst):
    self.list = lst
    self.marks = {}
    for marks, _ in lst:
      for mark in marks:
        self.marks[mark] = 1

  def find(self, ind):
    cur = ind.find_marks(self.marks)
    found = False
    for marks, key in self.list:
      ok = True
      for mark in marks:
        if mark not in cur:
          ok = False
          break
      if ok:
        if found:
          raise BaseException("Collision detected in Partition.find")
        found = key
    if not found:      
      raise BaseException("Partition not found for ind "+str(ind))
    return found    

class PartitionChecker:
  def __init__(self, partition):
    self.partition = partition
    self.l = {}
  def add(self, ind, k):
    try:
      d = extract_vars(self.partition.find(ind), k)
    except BaseException as e:
      print(ind)
      raise e
    v_id = vars_to_id(k)
    if v_id in self.l:
      if self.l[v_id] != d:
        raise BaseException("Partition checker failed "+str(v_id)+", "+str(self.l[v_id])+", "+str(d))
    else:
      self.l[v_id] = d

# All keys in block have same variables
class MapBlock:
  def __init__(self, d, l):
    self.l = l
    self.inds = sorted(d.keys())
    l_keys = norm_list([d[ind][0] for ind in self.inds])
    l_vals = norm_list([d[ind][1] for ind in self.inds])
    self.s = ",".join(ind.s + ":" + k.s+'='+v.s for ind, (k, v) in zip(self.inds, zip(l_keys, l_vals)))
    self.d = dict(zip(self.inds, zip(l_keys, l_vals)))
  def __hash__(self):
    return hash(self.s)
  def __eq__(self, other):
    return self.s == other.s
  def has(self, ind):
    return ind in self.d
  def get(self, ind, k, partition, var_gen):
    ind_b = None
    for ind_b_i in self.d:
      ind_b = ind_b_i
      break
    key_b = self.d[ind_b][0]
    key_b_p = partition.find(ind_b)
    key_p = partition.find(ind)

    if vars_to_id(key_b_p)!=vars_to_id(key_p):
      return False

    var_b_2_p = extract_vars(key_b_p, key_b)
    var_p_2_k = extract_vars(k, key_p)
    var_b_2_k = {}
    for v_b, v_p in var_b_2_p.items():
      if v_p.name not in var_p_2_k:
        print([str(bk)+"->"+str(pk) for bk, pk in var_b_2_p.items()])
        print([str(bk)+"->"+str(pk) for bk, pk in var_p_2_k.items()])
        raise BaseException("Cannot find a link between block ("+self.s+"), partition ("+str(key_p)+") and key ("+str(k)+") for variable \"" + str(v_p)+"\"")
      var_b_2_k[v_b] = var_p_2_k[v_p.name]
#    print(str(var_b_2_p.keys())+" -> "+str(var_p_2_k.keys())+"="+str(var_b_2_k.keys()))
    var_dict = var_b_2_k
    l_keys = norm_list([self.d[ind][0] for ind in self.inds], v=var_gen, d=var_dict)
    l_vals = norm_list([self.d[ind][1] for ind in self.inds], v=var_gen, d=None)
#    print(str(l_keys)+" = "+str(l_vals)+":"+str(self.inds))
    res = zip(self.inds, l_keys, l_vals)
#    print(str(res.keys()))
    return res

class MapStore:
  def __init__(self, t, blocks = None, d = None, identifier = 0, partition = None):
    if partition is None:
      partition = Partition([])
    self.partition = partition
    self.blocks = {} if blocks is None else blocks
    self.d = [] if d is None else d
    self.t = t
    self.fApplied = None
    self.identifier = identifier
    self.vars_by_layer = {}

  @cached_property
  def layers(self):
    layers = {}
    try:
      for _, k, _ in self.d:
        layers[vars_to_id(k)] = 1
    except BaseException as e:
      print(self.d)
      raise e
    return layers

  def term(self):
    return self.t

  def replace_term(self, addr, v):
    self.t = self.t.replace(addr, v)

  def refine_by_vars(self, bound_vars):
    new_blocks = {}
    remove_inds = []
    next_d = []
    for _, (ind, k, v) in enumerate(self.d):
      if not k.has_other_vars(bound_vars):
        next_d.append((ind, k, v))
        continue
      if v != c0:
        new_blocks.setdefault(vars_to_id(k), {})[ind] = (k, v)
      remove_inds.append(ind)
    self.d = next_d
    for i, d in new_blocks.items():
      if not d:
        continue
      block = MapBlock(d, i[0])
      self.blocks[block.s] = block
  
  def box(self, l):
    for _, (_, k, v) in enumerate(self.d):
      l.append(TermBox(k))
      l.append(TermBox(v))

  def unbox(self, l, forbid_deg=False):
    for i in reversed(range(len(self.d))):
      v = l.pop().term()
      k = l.pop().term()
      ind, k_old, v_old = self.d[i]
      if forbid_deg:
        if not k_old.is_same(k):
          raise BaseException("Degradation in memory (key) found from "+str(k_old)+" to "+str(k))
        if not v_old.is_same(v):
          raise BaseException("Degradation in memory (val) found from "+str(v_old)+" to "+str(v))
#      print([str(t) for t in [ind, k, v, k_old, v_old]])
      self.d[i] = ind, k, v

  def applyList(self, l, forbid_deg=False):
    nxt = []
    for fOne in l: self.applyTerm(fOne, forbid_deg=forbid_deg).appendToList(nxt)
    return nxt
  
  def applyTerm(self, f, forbid_deg=False, save_f_applied=False):
    nxt = self.clone()
    extra = []
    nxt.box(extra)
    nxt.t = termTermApply(f, self.t, extra=tuple(extra))
    nxt.unbox(extra, forbid_deg=forbid_deg)
    nxt.refine_by_vars(nxt.t.fillVars())
    if save_f_applied:
      nxt.fApplied = f
    return nxt

  def appendToList(self, l):
    if self.t.isEmpty() or self.isInList(l):
      return l
    l.append(self)
    return l

  @staticmethod
  def extendFunc(f):
    return f

  @staticmethod
  def extendTerm(t, addr):
    return t

  def isInOne(self, other):
    if not self.t.s==other.t.s:
      return False
    if not self.d == other.d:
      return False
    if not self.blocks.keys() == other.blocks.keys():
      return False
    return True
  
  def isInList(self, l):
    for m in l:
      if self.isInOne(m): return True
    return False    
  
  def check(self, k):
    return vars_to_id(k) in self.layers

  # get_by_ind and set_by_ind should be invoked only after check
  def get_by_ind(self, ind, key):
    for _, (ind_i, key_i, val_i) in enumerate(self.d):
      if ind_i==ind and key_i==key:
        return val_i
    if not self.check(key):
      raise BaseException("Get by ind not initialized (key="+str(ind)+")")
    return c0
  def put_key_val_by_ind(self, ind, key, val):
    for i, (ind_i, key_i, _) in enumerate(self.d):
      if ind==ind_i and key==key_i:
        self.d[i] = (ind, key, val)
        return self
    self.d.append((ind, key, val))
    return self

  def load_block(self, ind, key, block):
    update_vals = block.get(ind, key, self.partition, VarGenFromDict(self.t.fillVars()))
    if not update_vals:
      return False
    self.d.extend(update_vals)
    if not self.check(key):
      raise BaseException("Generated IterMap fails check(key) "+str(ind)+": "+str(key) + " in block "+block.s + " update_vals="+str(update_vals.keys()))
    return self
  
  def clone(self):
    return MapStore(
      self.t, 
      blocks=self.blocks.copy(), 
      d=self.d.copy(), 
      identifier=self.identifier, 
      partition=self.partition
    )

  def enum_all_possibilities(self, ind, k):
    checker = PartitionChecker(self.partition)
#    print('checker add '+str(ind)+' '+str(k))
    checker.add(ind, k)
    
    for _, (ind_other, k_other, _) in enumerate(self.d):
#      print('checker add '+str(ind_other)+' '+str(k_other))
      checker.add(ind_other, k_other)
    if self.check(k):
      return [self.clone()]
    others = [self.clone().put_key_val_by_ind(ind, k, c0)]
    l, _ = vars_to_id(k)
    for _, block in self.blocks.items():
      if block.l == l:
        loaded_block = self.clone().load_block(ind, k, block)
        if loaded_block:
          others.append(loaded_block)
    return others
    
  
