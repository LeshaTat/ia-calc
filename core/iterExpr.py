from .term import func, cortege, Var, Const, Func, pair
from .notation import *
from .iterAlgebra import IterItem

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
  def locSub(self, n, a):
    return self.loc(n, DownMes(a))
  def locOut(self, a):
    return self.loc(len(self.line), a)
  def locAddr(self, a):
    return self.loc(self.addr, DownMes(a))
  def toA(self, l):
    p = []
    if self.parent is None:
      p.append(func( 
        StateMes(c0, OutMes(self.loc(l, a))), 
        StateMes(self.scoord, OutMes(self.locAddr(self.locOut(a))))
      ))
      p.append(func( 
        StateMes(self.scoord, OutMes(self.locAddr(self.locOut(a)))), 
        StateMes(c0, OutMes(self.loc(l, a)))
      ))
    for j, sub in enumerate(self.line):
      p.append(func( 
        StateMes(
          self.scoord, 
          OutMes(self.locAddr(self.locSub(j, a)))
        ), 
        StateMes(
          sub.scoord, 
          OutMes(sub.locAddr(sub.locOut(a)))
        )
      ))
      p.append(func( 
        StateMes(
          sub.scoord, 
          OutMes(sub.locAddr(sub.locOut(a)))
        ), 
        StateMes(
          self.scoord, 
          OutMes(self.locAddr(self.locSub(j, a)))
        )
      ))
#        p = [strTerm(t) for t in p]
    for sub in self.line:
      p.extend( sub.toA(l) )
    return p

def automaton_expression(t, l=None):
    d = Diag(t)
    return IterItem(d.toA( l if l is not None else d.maxAddr() + 1 ))