from .term import func, cortege, Var, Const, Func
from .notation import *
from .termAlgebra import listO, listApply, U, listIntersect
from .iterRule import IterVarNode, IterFuncNode, IterRuleNode, iterRuleToAutomaton
from .operator import Operator

x = Var('x')
y = Var('y')
a = Var('a')
s = Var('s')
s0 = Var('s0')
sn = Var('sn')
k = Var('k')
v = Var('v')
p = Var('p')
d = Var('d')
k2 = Var('k2')

cUpArg = Const('upArg')
cDownArg = Const('downArg')
StateUp = Func('StateUp', 1)
StateUpDown = Func('StateUpDown', 2)

def ruleM(kList):
  n = len(kList)
  rule = [
    func(
      Input(a),
      Call(arr(c0, n), c0, StateMes(c0, OutMes(a)))
    ),
    func(
      Ret(
        arrList([s, *[Const("s"+str(i+1)) for i,k in enumerate(kList)]]),
        c0,
        StateMes(c0, OutMes(a))
      ),
      Output(a)
    ),
    *[
      func(
        Ret(
          arrList([s, *[Const("s"+str(i+1)) for i,k in enumerate(kList)]]),
          c0,
          StateMes(sn, CallMes(k, a))
        ),
        Call(
          arrList([sn, *[Const("s"+str(i+1)) for i,k in enumerate(kList)]]),
          k,
          StateMes(Const("s"+ str(i+1)), a)
        )
      )
      for i,k in enumerate (kList)
    ],
    *[
      func(
        Call(
          arrList([s, *[Const("s"+str(i+1)) for i,k in enumerate(kList)]]),
          k,
          StateMes(sn, y)
        ),
        Ret(
          arrList([s, *[
            Const("s"+str(iS+1)) if iS!=i else sn
            for iS,kS in enumerate(kList)
          ]]),
          c0,
          StateMes(s, CallMes(k, y))
        )
      )
      for i,k in enumerate (kList)
    ]
  ]
  return rule

icomp = [
  '0 ; 0 (0 x) -> 0 ; 1 1 (0 (0 x))',
  '0 ; 1 1 (0 (0 y)) -> 0 ; 0 (0 y)',
  '0 ; 1 1 (0 (1 x)) -> 0 ; 1 2 (0 x)',
  '0 ; 1 2 (0 y) -> 0 ; 1 1 (0 (1 y))',
  '0 ; 1 1 (1 k x) -> 1 ; 0 (1 k x)',
  '1 ; 0 (1 k y) -> 0 ; 1 1 (1 k y)',
  '0 ; 1 2 (1 k x) -> 2 ; 0 (1 k x)',
  '2 ; 0 (1 k y) -> 0 ; 1 2 (1 k y)'  
]

cTestArg = Const('testArg')
StateInterCall = Func('StateInterCall', 2)
StateInterOut = Func('StateInterOut', 1)
testInteractorRuleOld = [
  func(
    Input(StateMes(StateInterOut(s), OutMes(a))),
    Call(c0, cTestArg, StateMes(s, OutMes(a)))
  ),
  func(
    Input(StateMes(StateInterCall(s, k), CallMes(k, a))),
    Call(c0, cTestArg, StateMes(s, CallMes(k, a)))
  ),
  func(
    Ret(c0, cTestArg, StateMes(s, OutMes(a))),
    Output(StateMes(StateInterOut(s), OutMes(a)))
  ),
  func(
    Ret(c0, cTestArg, StateMes(s, CallMes(k, a))),
    Output(StateMes(StateInterCall(s, k), CallMes(k, a)))
  )
]
testInteractorRule = [
  func(
    Input(StateMes(StateInterOut(s), OutMes(a))),
    Call(c0, cTestArg, StateMes(s, OutMes(a)))
  ),
  func(
    Input(StateMes(StateInterCall(s, k), CallMes(k, a))),
    Call(c0, cTestArg, StateMes(s, CallMes(k, a)))
  ),
  func(
    Ret(c0, cTestArg, StateMes(s, OutMes(a))),
    Output(StateMes(StateInterOut(s), OutMes(a)))
  ),
  func(
    Ret(c0, cTestArg, StateMes(s, CallMes(k, a))),
    Output(StateMes(StateInterCall(s, k), CallMes(k, a)))
  )
]
UpCallState2 = Func('UpCallState', 2)
DownCallState = Func('DownCallState', 2)
icompRule = [
  func(
    Input(StateMes(c0, OutMes(a))),
    Call(c0, cUpArg, StateMes(c0, OutMes(UpMes(a))))
  ),
  func(
    Input(StateMes(pair(s, d), OutMes(a))),
    Call(d, cUpArg, StateMes(s, OutMes(UpMes(a))))
  ),
  func(
    Ret(d, cUpArg, StateMes(s, OutMes(UpMes(a)))),
    Output(StateMes(pair(s, d), OutMes(a)))
  ),
  func(
    Ret(d, cUpArg, StateMes(s, OutMes(DownMes(a)))),
    Call(s, cDownArg, StateMes(d, OutMes(a)))
  ),
  func(
    Ret(s, cDownArg, StateMes(d, OutMes(a))),
    Call(d, cUpArg, StateMes(s, OutMes(DownMes(a))))
  ),
  func(
    Ret(d, cUpArg, StateMes(s, CallMes(k, a))),
    Output(StateMes(UpCallState2(s, d), CallMes(k, a)))
  ),
  func(
    Input(StateMes(UpCallState2(s, d), CallMes(k, a))),
    Call(d, cUpArg, StateMes(s, CallMes(k, a)))
  ),
  func(
    Ret(s, cDownArg, StateMes(d, CallMes(k, a))),
    Output(StateMes(DownCallState(s, d), CallMes(k, a)))
  ),
  func(
    Input(StateMes(DownCallState(s, d), CallMes(k, a))),
    Call(s, cDownArg, StateMes(d, CallMes(k, a)))
  )
]
UpCallState = Func('UpCallState', 1)
icompStateRule = [
  func(
    Input(StateMes(s, OutMes(a))),
    Call(c0, cUpArg, StateMes(s, OutMes(UpMes(a))))
  ),
  func(
    Ret(c0, cUpArg, StateMes(s, OutMes(UpMes(a)))),
    Output(StateMes(s, OutMes(a)))
  ),
  func(
    Ret(c0, cUpArg, StateMes(s, OutMes(DownStateMes(d, a)))),
    Call(s, cDownArg, StateMes(d, OutMes(a)))
  ),
  func(
    Ret(s, cDownArg, StateMes(d, OutMes(a))),
    Call(c0, cUpArg, StateMes(s, OutMes(DownStateMes(d, a))))
  ),
  func(
    Ret(c0, cUpArg, StateMes(s, CallMes(k, a))),
    Output(StateMes(UpCallState(s), CallMes(k, a)))
  ),
  func(
    Input(StateMes(UpCallState(s), CallMes(k, a))),
    Call(c0, cUpArg, StateMes(s, CallMes(k, a)))
  ),
  func(
    Ret(s, cDownArg, StateMes(d, CallMes(k, a))),
    Output(StateMes(DownCallState(s, d), CallMes(k, a)))
  ),
  func(
    Input(StateMes(DownCallState(s, d), CallMes(k, a))),
    Call(s, cDownArg, StateMes(d, CallMes(k, a)))
  )
]
def printl(l):
  print("["+", ".join([str(t) for t in l])+"]")

class Interactor:
  def __init__(self):
    self.s0 = c0
    pass
  def getAutomaton(self):
    test = InteractorTest(self)
#    test = self
#    printl(test.getIterRule())
    return (test.s0, iterRuleToAutomaton(test.getIterRule()))
  def getNode(self):
    raise NotImplementedError
  def __call__(self, *args):
    if len(args)==1:
        return InteractorComposition(self, args[0])
    if len(args)>1:
        return self(args[0])(*args[1:])
    return self
  def compile(self):
    return self.getNode().addToRule()
  def print(self):
    printl(self.compile())
  def getIterRule(self, **kwargs):
    F = self.compile()
    FOp = Operator.const(F)
    h = Operator.v()
    iterOp = h.set( FOp.o( h.U([
      func(Input(x), Input(x)), 
      func(Ret(s, k, y), Ret(s, k, y))
    ]) ) )
    res = iterOp.calcFull()
    if "full" in kwargs:
      return res
    return listIntersect(res, [
      func(Input(x), Output(y)),
      func(Input(x), Call(s, k, y)),
      func(Ret(s, k, x), Call(d, k2, y)),
      func(Ret(s, k, x), Output(y))
    ])
  def calc(self):
    F = self.compile()
    FOp = Operator.const(F)
    h = Operator.v()
    iterOp = h.set( FOp.o( h.U([
      func(Input(x), Input(x)), 
      func(Ret(s, k, y), Ret(s, k, y))
    ]) ) )
    res = iterOp.calcFull()
    print('--o--')
    printl(F)
    print('--ori--')
    printl(res)
    print('--res--')
    printl(listIntersect(res, [
      func(Input(x), Output(y)),
      func(Input(x), Call(s, k, y)),
      func(Ret(s, k, x), Call(d, k2, y)),
      func(Ret(s, k, x), Output(y))
    ]))
    return   

class InterVarFull(Interactor):
  def __init__(self, v):
    self.vVar = v
    self.s0 = c0
    self.vNode = IterVarNode(v)
  def getNode(self):
    return self.vNode
  def __str__(self):
    return str(self.vVar)

class InterConst(Interactor):  
  def __init__(self, af):
    (self.s0, self.f) = af
    self.af = af
    self.fNode = IterFuncNode(self.f)
  def getNode(self):
    return self.fNode

class InterVar(InterConst):
  def __init__(self, v):
    super().__init__((c0, [
      func(
        StateMes(c0, OutMes(a)),
        StateMes(c0, CallMes(v, a))
      ),
      func(
        StateMes(c0, CallMes(v, a)),
        StateMes(c0, OutMes(a))
      )
    ]))
    self.vVar = v
  def __str__(self):
    return str(self.vVar)

class InteractorComposition(Interactor):
  def __init__(self, f, g):
    self.f = f
    self.g = g
    self.s0 = c0 #pair(self.f.s0, self.g.s0)
    self.comp = False
  def getNode(self):
    if self.comp is False:
      self.comp = IterRuleNode(
        icompStateRule,
#        icompRule,
        dict([
          (cUpArg, self.f.getNode()), (cDownArg, self.g.getNode())
        ])
      )
    return self.comp

class InteractorTest(Interactor):
  def __init__(self, f):
    self.f = f
    self.s0 = StateInterOut(self.f.s0)
    self.comp = False
  def getNode(self):
    if self.comp is False:
      self.comp = IterRuleNode(
        testInteractorRule,
        dict([
          (cTestArg, self.f.getNode())
        ])
      )
    return self.comp
