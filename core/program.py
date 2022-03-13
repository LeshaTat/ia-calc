from .iterProg import Call
from .iterRule import iterRuleToAutomaton
from .termAlgebra import listIntersect
from .term import func, cortege, Var, Const, Func
from .notation import *
from enum import Enum
from .operator import Operator
from .interactorAlgebra import InterConst

def printl(l):
  print('[')
  for t in l:
    print(str(t))
  print(']')

x = Var('x')
y = Var('y')
s = Var('s')
k = Var('k')

PosVarsInp = Func('PosVarsInp', 3)
StateVars = Func('StateVars', 1)
PosBranchPos = Func('PosBranchPos', 2)

class VarType(Enum):
  LEFT = 1
  RIGHT = 2

class VarsContext:
  def __init__(self):
    self.vars = {}
    self.vInd = 1
    self.varsAr = []
    self.varsStateAr = []
    self.inputVar = None;
  def remove(self, v):
    if v in self.vars: del self.vars[v]
  def addLeft(self, v):
    if( v in self.vars ): return
    self.vars[v] = VarType.LEFT
  def addRight(self, v):
    if( v in self.vars ): return
    self.vars[v] = VarType.RIGHT
  def addBranches(self, branches):
    #TODO: Add VarType.SUPPOSED_RIGHT type for the case when there are branches without the var. 
    bvars = {}
    for branch in branches:
      for (k, v) in branch.vars.items():
        if k not in bvars:
          bvars[k] = v
          continue
        if v == VarType.RIGHT:
          bvars[k] = v
    for (k, v) in bvars.items():
      if( k not in self.vars ):
        self.vars[k] = v
  def prepareVars(self):
    self.varsAr = []
    self.varsStateAr = []
    for (k, v) in self.vars.items():
      if v==VarType.RIGHT:
        self.varsStateAr.append(k)
        self.varsAr.append(k)
      else:
        self.varsAr.append(k)
    self.inputVar = self.genNewVar('inp')
  def genNewVar(self, s='v'):
    v = Var(s)
    while v in self.vars:
      v = vN(self.vInd)
      self.vInd+=1
    return v    
    
class Context:
  def __init__(self, vctx, fpos=None, prevPos=None):
    if fpos is None:
      fpos = lambda x: x
    self.fpos = fpos
    self.vctx = vctx
    self.prevPos = prevPos
    self.nUp = 0
  def makePos(self, line):
    if isinstance(line, list):
      return cortege(*[cN(i) for i in line])
    return cN(line)
  def makePosVarsInp(self, line, d={}, inp=None):
    return PosVarsInp(self.makePos(line), cortege(*[
      v if v not in d else d[v] for v in self.vctx.varsAr
    ]), self.vctx.inputVar if inp is None else inp(self.vctx.inputVar))
  def makeStateVars(self, d={}):
    return StateVars(cortege(*[
      v if v not in d else d[v] for v in self.vctx.varsStateAr
    ]))
  def makePosVars0Inp(self, line):
    return PosVarsInp(self.makePos(line), cortege(*[
      c0 for v in self.vctx.varsAr
    ]), self.vctx.inputVar)
  def makePosVarsInpFromState(self, line):
    return PosVarsInp(self.makePos(line), cortege(*[
      v if v in self.vctx.varsStateAr else c0 for v in self.vctx.varsAr
    ]), self.vctx.inputVar)
    

class ProgVar:
  def __init__(self, name):
    self.name = name

def nUpA(n, a):
  if n==0:
    return a
  else:
    return UpMes(nUpA(n-1, a))
    
class Program:
  def __init__(self, argsN, makeList):    
    self.argsN = argsN
    self.list = makeList(*range(argsN))
  def build(self):
    vctx = VarsContext()
    self.fillVars(vctx)
    vctx.prepareVars()
    ctx = Context(vctx)
    ctx.nUp = self.argsN
#    print([str(t) for t in vctx.varsAr])
#    print([str(t) for t in vctx.varsStateAr])
    ar = []
    self.addIterRules(ar, ctx)
    return ar
  def compile(self):
    return InterConst((c0, self.toAutomaton()))
  def toAutomaton(self):
    FOp = Operator.const(self.build())
    h = Operator.v()
    iterOp = h.set( FOp.o( h.U([
      func(Input(x), Input(x)) 
    ]) ) )
    res = iterOp.calcFull()
#    printl(res)
    return iterRuleToAutomaton(
      res
    )
#    print(
#      listIntersect(res, [
#        func(Input(x), Output(y)),
#        func(Input(x), Call(s, k, y))
#      ])
#    )
  def addIterRules(self, ar, ctx):
    ar.append(
      func(
        Input(StateMes(c0, OutMes(nUpA(ctx.nUp, ctx.vctx.inputVar)))),
        Run(ctx.makePosVars0Inp(0))
      )
    )
    ar.append(
      func(
        Input(StateMes(ctx.makeStateVars(), OutMes(nUpA(ctx.nUp, ctx.vctx.inputVar)))),
        Run(ctx.makePosVarsInpFromState(0))
      )
    )
    for (i, op) in enumerate(self.list):
      op.addIterRules(ar, ctx, i, i+1, 0)
  def fillVars(self, vctx):
    for op in self.list:
      op.fillVars(vctx)

class ProgOperator:
  def addIterRules(self, ar, ctx, lineFrom, lineTo, lineBack):
    pass

def printd(d):
  for (k, v) in d.items():
    print(k,':',v)
class MessageOperator(ProgOperator):
  def __init__(self, pattern):
    self.pattern = pattern
  def fillVars(self, vctx):
    self.pattern.fillVars(VarType.LEFT, vctx.vars)
  def addIterRules(self, ar, ctx, lineFrom, lineTo, lineBack):
    patternVars = self.pattern.fillVars(lambda v: ctx.vctx.genNewVar(str(v)))
    ar.append(
      func(
        Run(ctx.makePosVarsInp(lineFrom, patternVars, lambda inp: self.pattern)),
        Run(ctx.makePosVarsInp(lineTo, {}, lambda inp: self.pattern))
      )
    )

class ReturnOperator(ProgOperator):
  def __init__(self, pattern):
    self.pattern = pattern
  def fillVars(self, vctx):
    self.pattern.fillVars(VarType.RIGHT, vctx.vars)
  def addIterRules(self, ar, ctx, lineFrom, lineTo, lineBack):
    ar.append(
      func(
        Run(ctx.makePosVarsInp(lineFrom)),
        Output(StateMes(ctx.makeStateVars(), OutMes(nUpA(ctx.nUp, self.pattern))))
      )
    )

class ParseOperator(ProgOperator):
  def __init__(self, pattern, v):
    self.v = v
    self.pattern = pattern
  def fillVars(self, vctx):
    vctx.addRight(self.v)
    self.pattern.fillVars(VarType.LEFT, vctx.vars)
  def addIterRules(self, ar, ctx, lineFrom, lineTo, lineBack):    
    patternVars = self.pattern.fillVars(lambda v: ctx.vctx.genNewVar(str(v)))
    patternVars[self.v] = self.pattern
    ar.append(
      func(
        Run(ctx.makePosVarsInp(lineFrom, patternVars)),
        Run(ctx.makePosVarsInp(lineTo))
      )
    )

class SetOperator(ProgOperator):
  def __init__(self, v, pattern):
    self.v = v
    self.pattern = pattern
  def fillVars(self, vctx):
    self.pattern.fillVars(VarType.RIGHT, vctx.vars)
    vctx.addLeft(self.v)
  def addIterRules(self, ar, ctx, lineFrom, lineTo, lineBack):    
    d = {}
    d[self.v] = self.pattern
    ar.append(
      func(
        Run(ctx.makePosVarsInp(lineFrom)),
        Run(ctx.makePosVarsInp(lineTo, d))
      )
    )

class CallOperator(ProgOperator):
  def __init__(self, v, func, arg):
    self.v = v
    self.func = func
    self.arg = arg
  def fillVars(self, vctx):
    self.arg.fillVars(VarType.RIGHT, vctx.vars)
    vctx.addLeft(self.v)
  def addIterRules(self, ar, ctx, lineFrom, lineTo, lineBack):    
    ar.append(
      func(
        Run(ctx.makePosVarsInp(lineFrom)),
        Call(ctx.makePosVarsInp(lineFrom), self.func, self.arg)
      )
    )
    ar.append(
      func(
        Ret(ctx.makePosVarsInp(lineFrom), self.func, self.v),
        Run(ctx.makePosVarsInp(lineTo))
      )
    )

def nUpDownA(n, s, a):
  return nUpA(n, DownStateMes(s, a))

class CallInteractorOperator(ProgOperator):
  def __init__(self, v, func, svar, arg):
    self.v = v
    self.func = func
    self.svar = svar
    self.arg = arg
  def fillVars(self, vctx):
    self.arg.fillVars(VarType.RIGHT, vctx.vars)
    vctx.addRight(self.svar)
    vctx.addLeft(self.v)
    vctx.addLeft(self.svar)
  def addIterRules(self, ar, ctx, lineFrom, lineTo, lineBack):
    ar.append(
      func(
        Run(ctx.makePosVarsInp(lineFrom)),
        Output(StateMes(ctx.makePosVarsInp(lineFrom), OutMes(nUpDownA(self.func, self.svar, self.arg))))
      )
    )
    dFr = {}
    dFr[self.svar] = ctx.vctx.genNewVar(str(self.svar))
    d = {}
    a = ctx.vctx.genNewVar('a')
    d[self.v] = a
    ar.append(
      func(
        Input(StateMes(ctx.makePosVarsInp(lineFrom, dFr), OutMes(nUpDownA(self.func, self.svar, a)))),
        Run(ctx.makePosVarsInp(lineTo, d))
      )
    )

def listify(o):
  if isinstance(o, list): return o
  return [o]

class TestOperator(ProgOperator):
  def __init__(self, vars, vals):    
    self.vals = vals
    if not isinstance(self.vals, list):
      self.vals = [self.vals]
    self.vals = [listify(o) for o in self.vals]
    self.vars = vars
    if not isinstance(self.vars, list):
      self.vars = [self.vars]
  def fillVars(self, vctx):
    for v in self.vars:
      vctx.addRight(v)
  def addIterRules(self, ar, ctx, lineFrom, lineTo, lineBack):
    cur = [0 for k in self.vals]
    valsCount = len(self.vals)
    while True:
      d = {}
      for i, v in enumerate(self.vars):
        d[v] = self.vals[i][cur[i]]
      ar.append(
        func(
          Run(ctx.makePosVarsInp(lineFrom, d)),
          Run(ctx.makePosVarsInp(lineTo, d))
        )
      )
      pos = 0
      while pos<valsCount and cur[pos]==len(self.vals[pos])-1:
        cur[pos] = 0
        pos = pos+1
      if pos>=valsCount:
        break
      cur[pos] = cur[pos] + 1

class BranchesOperator(ProgOperator):
  def __init__(self, branches):
    self.branches = branches
  def fillVars(self, vctx):
    branchesCtx = []
    for branch in self.branches:
      bvctx = VarsContext()
      branchesCtx.append(bvctx)
      for op in branch:
        op.fillVars(bvctx)
    vctx.addBranches(branchesCtx)
  def addIterRules(self, ar, ctx, lineFrom, lineTo, lineBack):
    lineBase = listify(lineFrom)
    for (i, branch) in enumerate(self.branches):
      lineZero = lineBase + [i]
      ar.append(
        func(
          Run(ctx.makePosVarsInp(lineFrom)),
          Run(ctx.makePosVarsInp(lineZero+[0]))
        )
      )
      for (j, op) in enumerate(branch):
        op.addIterRules(ar, ctx,
          lineZero + [j],
          lineZero + [(j+1)] if j+1<len(branch) else lineTo,
          lineFrom
        )

class BackOperator(ProgOperator):        
  def fillVars(self, vctx):
    pass
  def addIterRules(self, ar, ctx, lineFrom, lineTo, lineBack):
    ar.append(
      func(
        Run(ctx.makePosVarsInp(lineFrom)),
        Run(ctx.makePosVarsInp(lineBack)),
      )
    )
