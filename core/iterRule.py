from .iterProg import Call
from .term import func, Var, Const, Func, pair
from .notation import *
from .termAlgebra import listO, listApply, U

x = Var('x')
y = Var('y')
a = Var('a')
s = Var('s')
s0 = Var('s0')
k = Var('k')
v = Var('v')
p = Var('p')

Sub = Func('Sub', 2)
ACall = Func('ACall', 1)
BCall = Func('BCall', 1)

def iterRuleToAutomaton(rule):
  inp = [
    func(
      StateMes(s, OutMes(a)),
      Input(StateMes(s, OutMes(a)))
    ),
    func(
      StateMes(ACall(s), CallMes(k, a)),
      Input(StateMes(s, CallMes(k, a)))
    ),
    func(
      StateMes(BCall(s), CallMes(k, a)),
      Ret(s, k, a)
    ),
  ]
  outp = [
    func(
      Output(StateMes(s, OutMes(a))),
      StateMes(s, OutMes(a))
    ),
    func(
      Output(StateMes(s, CallMes(k, a))),
      StateMes(ACall(s), CallMes(k, a))
    ),
    func(
      Call(s, k, a),
      StateMes(BCall(s), CallMes(k, a))
    )
  ]
  return listO(outp, listO(rule, inp))

class IterNode:
  def __init__(self):
    pass
  def addToRule(self, k=None, prefix=None):
    raise NotImplementedError

StatePrefix = Func('StatePrefix', 2)
StateStatePrefix = Func('StateStatePrefix', 3)
class IterVarNode(IterNode):
  def __init__(self, v):
    self.v = v
  def addToRule(self, k=None, prefix=None):
    if k is None:
      return [
        func(
          Input(a),
          Call(c0, self.v, a)
        ),
        func(
          Ret(c0, self.v, a),
          Output(a)
        )
      ]

    return [
      func(
        Sub(StatePrefix(s0, prefix), Call(s, k, a)),
        Call(StateStatePrefix(s0, s, prefix), self.v, a)
      ),
      func(
        Ret(StateStatePrefix(s0, s, prefix), self.v, a),
        Sub(StatePrefix(s0, prefix), Ret(s, k, a))
      )
    ]

class IterFuncNode(IterNode):
  def __init__(self, f):
    self.f = f
  def addToRule(self, k=None, prefix=None):
    if k is None:
      return func(
        func(x, y),
        func(Input(x), Output(y))
      )(self.f)

    return func( 
      func(x, y),
      func(
        Sub(StatePrefix(s0, prefix), Call(s, k, x)), 
        Sub(StatePrefix(s0, prefix), Ret(s, k, y))
      )
    )(self.f)
SPair = Func('SPair', 2)
PPair = Func('PPair', 2)
class IterRuleNode(IterNode):
  def __init__(self, F, childs):
    self.F = F
    self.childs = childs
  def addToRule(self, k=None, prefix=None):
    if k is None:
      cur = c0
    else:
      cur = PPair(prefix, k)
    rule1 = func( 
      func(x, y),
      func(
        Sub(StatePrefix(s, cur), x),
        Sub(StatePrefix(s, cur), y)
      )
    )(self.F)
    if k is not None:
      rule2 = [
        func(
          Sub(StatePrefix(s0, prefix), Call(s, k, a)),
          Sub(StatePrefix(SPair(s0, s), cur), Input(a))
        ),
        func(
          Sub(StatePrefix(SPair(s0, s), cur), Output(a)),
          Sub(StatePrefix(s0, prefix), Ret(s, k, a))
        )
      ]
    else:
      rule2 = [
        func(
          Input(a),
          Sub(StatePrefix(c0, cur), Input(a))
        ),
        func(
          Sub(StatePrefix(c0, cur), Output(a)),
          Output(a)
        )
      ]
    rule = U(rule1, rule2)
    #print('--r1--', strTerm(cur))
    #printListAsRel(rule1)
    #print('--r2--')
    #printListAsRel(rule2)
    for kChild, child in self.childs.items():
      ruleK = child.addToRule(kChild, cur)
      #print('--rk-- cur=', strTerm(cur), "k=", strTerm(kChild))
      #printListAsRel(ruleK)
      rule = U(
        rule,
        ruleK
      )
    return rule
