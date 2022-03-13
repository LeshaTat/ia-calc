from .termAlgebra import listSimplify, U, UInc, listO
from .term import Var, Const, func
from enum import Enum
class NodeStatus(Enum):
  IDLE = 0
  CHANGED = 1
  PROCESS = 2
  DONE = 3

class Node:
  def __init__(self):
    self.status = NodeStatus.IDLE
    self.inc = []
    self.prev = []
    self.cur = []
    self.args = []
    self.h = None
  def calc(self, h):
    if self.status is NodeStatus.PROCESS:
      return self.cur
    if self.status is NodeStatus.DONE:
      if self.h != h:
        self.inc = []
        self.prev = self.cur
      return self.cur
    if self.h == h:
      return self.cur
    self.h = h
    self.status = NodeStatus.PROCESS
    allDone = self.prepare(h)
    self.inc = []
    self.prev = self.cur
    self.calcSpecific()
    self.status = NodeStatus.DONE if allDone else NodeStatus.IDLE
    return self.cur
  def prepare(self, h):
    allDone = True
    for arg in self.args:
      if arg is None:
        raise Exception("".join(["Arg of ",str(self)," must not be None"]))
      arg.calc( h )
      allDone = False if arg.status is not NodeStatus.DONE else allDone
    return allDone
  def calcSpecific(self):
      """
      Calculate specific operation on self.args and write result in self.cur and self.inc
      """
      raise NotImplementedError

class IdentityNode(Node):
  def __init__(self, s, a1=None):
    Node.__init__(self)
    self.args = [a1]
  def calcSpecific(self):
    (self.cur, self.inc) = (self.args[0].cur, self.args[0].inc)

class ApplyNode(Node):
  def __init__(self, s, a1=None, amb=False):
    Node.__init__(self)        
    if not isinstance(a1, Node): raise Exception(str(self))
    self.amb = amb
    self.args = [a1]
    self.s = s
  def calcSpecific(self):
    inc = self.s.apply(self.args[0].inc)
    if self.amb:
        inc = listSimplify(inc)
    (self.cur, self.inc) = UInc(self.prev, inc)

#class TransitNode(ApplyNode):
#    def __init__(self, a1=None):
#      ApplyNode.__init__(self, "a b (c a (c b))", a1)

class ConstNode(Node):
  def __init__(self, v):
    Node.__init__(self)
    self.v = v
  def calcSpecific(self):
    self.inc = self.v
    self.cur = self.v

class CompositionNode(Node):
  def __init__(self, a1=None, a2=None):
    Node.__init__(self)
    if not isinstance(a1, Node): raise Exception(str(self))
    if not isinstance(a2, Node): raise Exception(str(self))
    self.args = [a1, a2]
  def calcSpecific(self):
    c1 = self.args[0].cur
    i1 = self.args[0].inc
    p2 = self.args[1].prev
    i2 = self.args[1].inc
    inc = listO(c1, i2)
    inc = U(inc, listO(i1, p2))
    (self.cur, self.inc) = UInc(self.prev, inc)

class UnionNode(Node):
  def __init__(self, a1=None, a2=None):
    Node.__init__(self)
    if not isinstance(a1, Node): raise Exception(str(self))
    if not isinstance(a2, Node): raise Exception(str(self))
    self.args = [a1, a2]
  def calcSpecific(self):
    inc = U(self.args[0].inc, self.args[1].inc)
    (self.cur, self.inc) = UInc(self.prev, inc)

class Operator:
  h = 0
  def __init__(self, node):
    if not isinstance(node, Node):
      raise Exception("Node must be Node")
    self.node = node
  @staticmethod
  def const(v):
    return Operator(ConstNode(v))
  @staticmethod
  def v(v=None):
    return Operator(IdentityNode(op(v).node if v is not None else None))
  def set(self, p, i=0):
    self.node.args[i] = op(p).node
    return self
  def cur(self):
    return self.node.cur
  def inc(self):
    return self.node.inc
  def apply(self, s, amb=False):
    return Operator(ApplyNode(s, self.node, amb))
#  def t(self):
#    return Operator(TransitNode(self.node))
  def U(self, p):
    return Operator(UnionNode(self.node, op(p).node))
  def o(self, p):
    return Operator(CompositionNode(self.node, op(p).node))
  def calc(self):
    Operator.h += 1
    return self.node.calc(Operator.h)
  def calcFull(self):
    self.calc()
    while len(self.node.inc)>0:
      self.calc()
    self.node.status = NodeStatus.DONE
    return self.node.cur
      

def op(v):
  if isinstance(v, list): return Operator.const(v)
  return v
  
def const(v):
  return Operator.const(v)
  
def var(v=None):
  return Operator.v(v)