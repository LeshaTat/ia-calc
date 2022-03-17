from enum import Enum
from .term import ID, func, cortege, Var, Const, Func, Term
from .iterAlgebra import IterItem
from .notation import *

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
    self.globalVars = {}
    self.vInd = 1
    self.varsAr = []
    self.varsStateAr = []
    self.inputVar = None;
  def derive(self):
    vc = VarsContext()
    vc.globalVars = self.globalVars
    return vc
  def remove(self, v):
    if v in self.vars: del self.vars[v]
  def addLeft(self, v):
    if v in self.vars: return
    self.vars[v] = VarType.LEFT
  def addRight(self, v):
    if v in self.vars: return
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
      if k not in self.vars:
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
    while v in self.globalVars:
      v = vN(self.vInd, s=s)
      self.vInd+=1
    self.globalVars[v] = 1
    return v

class VarsGenerator:
  def __init__(self, vctx):
    self.vctx = vctx
    self.d = {}
  def __call__(self, v):
    if v not in self.d:
      self.d[v] = self.vctx.genNewVar(v)
    return self.d[v]

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
      return ID(Const(".".join([str(i) for i in line])))
#      return cortege(*[cN(i) for i in line])
    return ID(cN(line))
  def makePosVarsInp(self, line, d=None, inp=None):
    if d is None: d = {}
    return PosVarsInp(self.makePos(line), cortege(*[
      v if v not in d else d[v] for v in self.vctx.varsAr
    ]), self.vctx.inputVar if inp is None else inp(self.vctx.inputVar))
  def makeStateVars(self, d=None):
    if d is None: d = {}
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
    return Up(nUpA(n-1, a))
    
class Program:
  def __init__(self, argsN, makeList):    
    self.argsN = argsN
    self.makeList = makeList
    self.list = []
  def build(self, print_desc=False):
    vctx = VarsContext()
    block = Block(self.makeList(VarsGenerator(vctx), *range(self.argsN)))
    block.fillVars(vctx)
    vctx.prepareVars()
    ctx = Context(vctx)
    ctx.nUp = self.argsN
    if print_desc:
      print([str(t) for t in vctx.varsAr])
      if vctx.varsStateAr:
        print("VAR STATES")
        print([str(t) for t in vctx.varsStateAr])
    ar = []
    ar.append(
      func(
        StateMesIn(c0, Out(nUpA(ctx.nUp, ctx.vctx.inputVar))),
        Iter(ctx.makePosVars0Inp(0))
      )
    )
    ar.append(
      func(
        StateMesIn(ctx.makeStateVars(), Out(nUpA(ctx.nUp, ctx.vctx.inputVar))),
        Iter(ctx.makePosVarsInpFromState(0))
      )
    )
    block.addIterRules(ar, ctx, 0, 1, 0)
    return IterItem(ar)

def program(argsN, makeList, print_desc=False):
  prog = Program(argsN, makeList)
  return prog.build(print_desc=print_desc)

class ProgOperator:
  def addIterRules(self, ar, ctx, lineFrom, lineTo, lineBack):
    pass

def printd(d):
  for (k, v) in d.items():
    print(k,':',v)

class Message(ProgOperator):
  def __init__(self, pattern):
    self.pattern = pattern
  def fillVars(self, vctx):
    self.pattern.fillVars(VarType.LEFT, vctx.vars)
  def addIterRules(self, ar, ctx, lineFrom, lineTo, lineBack):
    patternVars = self.pattern.fillVars(lambda v: ctx.vctx.genNewVar(str(v)))
    ar.append(
      func(
        Iter(ctx.makePosVarsInp(lineFrom, patternVars, lambda inp: self.pattern)),
        Iter(ctx.makePosVarsInp(lineTo, {}, lambda inp: c0))
      )
    )

class Return(ProgOperator):
  def __init__(self, pattern):
    self.pattern = pattern
  def fillVars(self, vctx):
    self.pattern.fillVars(VarType.RIGHT, vctx.vars)
  def addIterRules(self, ar, ctx, lineFrom, lineTo, lineBack):
    ar.append(
      func(
        Iter(ctx.makePosVarsInp(lineFrom)),
        StateMesOut(ctx.makeStateVars(), Out(nUpA(ctx.nUp, self.pattern)))
      )
    )

class Parse(ProgOperator):
  def __init__(self, pattern, v):
    if not v.isVar:
      raise BaseException("Variable in Parse must be a variable: "+str(v))
    self.v = v
    self.pattern = pattern
  def fillVars(self, vctx):
    vctx.addRight(self.v)
    self.pattern.fillVars(VarType.LEFT, vctx.vars)
  def addIterRules(self, ar, ctx, lineFrom, lineTo, lineBack):    
    resVars = {}
    patternVars = self.pattern.fillVars(lambda v: ctx.vctx.genNewVar(str(v)))
    if self.v not in patternVars:
      resVars[self.v] = self.pattern
    patternVars[self.v] = self.pattern
    ar.append(
      func(
        Iter(ctx.makePosVarsInp(lineFrom, patternVars)),
        Iter(ctx.makePosVarsInp(lineTo, resVars))
      )
    )

class Set(ProgOperator):
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
        Iter(ctx.makePosVarsInp(lineFrom)),
        Iter(ctx.makePosVarsInp(lineTo, d))
      )
    )

def nUpDownA(n, a):
  return nUpA(n, Down(a))

class Call(ProgOperator):
  def __init__(self, v, func, arg, mem=False):
    self.v = v
    self.func = func
    self.arg = arg
    self.mem = mem
  def fillVars(self, vctx):
    self.arg.fillVars(VarType.RIGHT, vctx.vars)
    if self.v.isVar:
      vctx.addLeft(self.v)
  def addIterRules(self, ar, ctx, lineFrom, lineTo, lineBack):
    if isinstance(self.func, Term):
      lib_wrapper = Lib
      if self.mem:
        lib_wrapper = Mem
      ar.append(
        func(
          Iter(ctx.makePosVarsInp(lineFrom)),
          StateMesOut(ctx.makePosVarsInp(lineFrom), lib_wrapper(self.func, self.arg))
        )
      )
      d = {}
      if self.v.isVar:
        a = ctx.vctx.genNewVar('a')
        d[self.v] = a
      else:
        a = self.v
      ar.append(
        func(
          StateMesIn(
            ctx.makePosVarsInp(lineFrom), 
            LibRet(self.func, a) if not self.mem else MemRet(a)
          ),
          Iter(ctx.makePosVarsInp(lineTo, d))
        )
      )
      return
    ar.append(
      func(
        Iter(ctx.makePosVarsInp(lineFrom)),
        StateMesOut(ctx.makePosVarsInp(lineFrom), Out(nUpDownA(self.func, self.arg)))
      )
    )
    dFr = {}
    d = {}
    if self.v.isVar:
      a = ctx.vctx.genNewVar('a')
      d[self.v] = a
    else:
      a = self.v
    ar.append(
      func(
        StateMesIn(ctx.makePosVarsInp(lineFrom, dFr), Out(nUpDownA(self.func, a))),
        Iter(ctx.makePosVarsInp(lineTo, d))
      )
    )

def listify(o):
  if isinstance(o, list): return o
  return [o]

class Test(ProgOperator):
  def __init__(self, vrs, vals):    
    self.vals = vals
    if not isinstance(self.vals, list):
      self.vals = [self.vals]
    self.vals = [listify(o) for o in self.vals]
    self.vars = vrs
    if not isinstance(self.vars, list):
      self.vars = [self.vars]
      if not vrs.isVar:
        raise BaseException("Variable in Test must be a variable: " + str(vrs))
    else:
      for v in vrs:
        if not v.isVar:
          raise BaseException("Variable in Test must be a variable: " + str(v))

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
          Iter(ctx.makePosVarsInp(lineFrom, d)),
          Iter(ctx.makePosVarsInp(lineTo, d))
        )
      )
      pos = 0
      while pos<valsCount and cur[pos]==len(self.vals[pos])-1:
        cur[pos] = 0
        pos = pos+1
      if pos>=valsCount:
        break
      cur[pos] = cur[pos] + 1

class Branches(ProgOperator):
  def __init__(self, branches):
    self.branches = [Block(branch) for branch in branches]
  def fillVars(self, vctx):
    branchesCtx = []
    for branch in self.branches:
      bvctx = vctx.derive()
      branchesCtx.append(bvctx)
      branch.fillVars(bvctx)
    vctx.addBranches(branchesCtx)
  def addIterRules(self, ar, ctx, lineFrom, lineTo, lineBack):
    lineBase = listify(lineFrom)
    for (i, branch) in enumerate(self.branches):
      lineZero = lineBase + [i]
      ar.append(
        func(
          Iter(ctx.makePosVarsInp(lineFrom)),
          Iter(ctx.makePosVarsInp(lineZero))
        )
      )
      branch.addIterRules(ar, ctx,
          lineZero,
          lineTo,
          lineFrom
        )

class Block(ProgOperator):
  def __init__(self, lst):
    self.list = lst
  def fillVars(self, vctx):
    subVctx = vctx.derive()
    for k, op in enumerate(self.list):
      while callable(op):
        op = op(VarsGenerator(subVctx))
      if isinstance(op, list):
        op = Block(op)
      self.list[k] = op
      op.fillVars(subVctx)
    vctx.addBranches([subVctx])
  def addIterRules(self, ar, ctx, lineFrom, lineTo, lineBack):
    lineBase = listify(lineFrom)
    ar.append(
      func(
        Iter(ctx.makePosVarsInp(lineFrom)),
        Iter(ctx.makePosVarsInp(lineBase+[0]))
      )
    )
    for (j, op) in enumerate(self.list):
#      if callable(op):
#        op = op(VarsGenerator(ctx.vctx))
#      if isinstance(op, list):
#        op = Block(op)
      op.addIterRules(ar, ctx,
        lineBase + [j],
        lineBase + [(j+1)] if j+1<len(self.list) else lineTo,
        lineBack
      )

class Back(ProgOperator):        
  def fillVars(self, vctx):
    pass
  def addIterRules(self, ar, ctx, lineFrom, lineTo, lineBack):
    ar.append(
      func(
        Iter(ctx.makePosVarsInp(lineFrom)),
        Iter(ctx.makePosVarsInp(lineBack)),
      )
    )

class Stop(ProgOperator):        
  def fillVars(self, vctx):
    pass
  def addIterRules(self, ar, ctx, lineFrom, lineTo, lineBack):
    pass
