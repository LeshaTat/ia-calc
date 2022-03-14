from .term import ID, Func, Const, Var, pair, empty, vN

def cN(n):
  return Const(str(n))
c0 = cN(0)
c1 = cN(1)
c2 = cN(2)
c3 = cN(3)
vN = vN

cInit = Const("init")
Iter = Func('Iter', 1)
Input = Func('Input', 1)
Output = Func('Output', 1)

Ret = Func('Ret', 3)
Run = Func('Run', 1)

StateMes = Func('StateMes', 2)
OutMes = Func('OutMes', 1)
CallMes = Func('CallMes', 2)
UpMes = Func('UpMes', 1)
DownMes = Func('DownMes', 1)
DownStateMes = Func('DownStateMes', 2)

UpState = Func("UpState", 2)
DownCallState = Func("DownCallState", 2)
IterUp = Func("IterUp", 2)
IterDown = Func("IterDown", 2)
State = Func("State", 1)

Mem = Func("Mem", 1)
cMem = Const("Mem")
SetByAddrValue = Func("SetByAddrValue", 2)
GetByAddr = Func("GetByAddr", 1)

StateSet = Func("StateSet", 3)
StateGet = Func("StateGet", 2)

mode0 = ID(c0)
mode1 = ID(c1)
mode2 = ID(c2)
mode3 = ID(c3)

""" def StateMesOut(a):
  return StateMes(c0, MesOut(a))
def StateMesSub(s, k, a):
  return StateMes(c0, MesSub(s, k, a))
 """

def arr(c, n=0):
  if n==0: return c
  return pair(arr(c, n-1), c)
def arrList(lst):
  if len(lst)==1 : return lst[0]
  if len(lst)==0 : return empty
  return pair(arrList(lst[:-1]), lst[-1])