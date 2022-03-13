from .term import func, cortege, Var, Const, Func, pair
from .notation import *
from .termAlgebra import listO, listApply, U, listIntersect
from .iterRule import IterVarNode, IterFuncNode, IterRuleNode
from .operator import Operator

a = Var('a')
s = Var('s')
d = Var('d')
sp = Var('sp')
DiagAddr = Func('DiagAddr', 1)
DiagSAddr = Func('DiagSAddr', 1)
StackPos = Func('StackPos', 2)
InitPos = Func('InitPos', 1)
SList = Func('SList', 2) 


def nUpA(n, a):
  if n==0:
    return a
  else:
    return UpMes(nUpA(n-1, a))

class Diag:
  def __init__(self, t, parent=None, addrs=None):
    if addrs is None: addrs = {}
    self.parent = parent
    self.line = []
    while isinstance(t, tuple):
      if len(t)>1:
        self.line.insert( 0, Diag(t[len(t)-1], self, addrs) )
        t = t[:-1]
      else:
        t = t[0]
    self.addr = t-1
    if self.addr in addrs:
      self.saddr = DiagSAddr(cN(addrs[self.addr]))
      addrs[self.addr] = addrs[self.addr]+1
    else:
      self.saddr = DiagSAddr(c0)
      addrs[self.addr] = 1
    coord = DiagAddr(cN(self.addr))
    self.scoord = coord if self.saddr==DiagSAddr(c0) else pair(self.saddr, coord)
          
  def maxAddr(self):
    return max([d.maxAddr() for d in self.line] + [self.addr])
  def loc(self, n, a):
    return nUpA(n, a)
  def locSub(self, n, s, a):
    return self.loc(n, DownStateMes(s, a))
  def locOut(self, a):
    return self.loc(len(self.line), a)
  def locAddr(self, s, a):
    return self.loc(self.addr, DownStateMes(s, a))
  def toA(self, l):
    p = []
    if self.parent is None:
      p.append(func( 
        StateMes(c0, OutMes(self.loc(l, a))), 
        StateMes(StackPos(c0, self.scoord), OutMes(self.locAddr(c0, self.locOut(a))))
      ))
      p.append(func( 
        StateMes(InitPos(s), OutMes(self.loc(l, a))), 
        StateMes(StackPos(c0, self.scoord), OutMes(self.locAddr(s, self.locOut(a))))
      ))
      p.append(func( 
        StateMes(StackPos(c0, self.scoord), OutMes(self.locAddr(s, self.locOut(a)))), 
        StateMes(InitPos(s), OutMes(self.loc(l, a)))
      ))
    for j, sub in enumerate(self.line):
      p.append(func( 
        StateMes(
          StackPos(sp, self.scoord), 
          OutMes(self.locAddr(s, self.locSub(j, d, a)))
        ), 
        StateMes(
          StackPos(SList(sp, s), sub.scoord), 
          OutMes(sub.locAddr(d, sub.locOut(a)))
        )
      ))
      p.append(func( 
        StateMes(
          StackPos(SList(sp, s), sub.scoord), 
          OutMes(sub.locAddr(d, sub.locOut(a)))
        ), 
        StateMes(
          StackPos(sp, self.scoord), 
          OutMes(self.locAddr(s, self.locSub(j, d, a)))
        )
      ))
#        p = [strTerm(t) for t in p]
    for sub in self.line:
      p.extend( sub.toA(l) )
    return p

def exprToF(t, l=None):
    d = Diag(t)
    return (c0, d.toA( l if l is not None else d.maxAddr()+1 ))