from core.iterDebug import runOnSeq
from core.iterExtract import lib_call_to_comp
from core.iterMap2 import Partition
from core.term import func, norm, Term, Func, Const, Var, termToStr
from core.notation import *
from core.iterAlgebra import comp, IterItem, iter_var
from core.iterProg import *
from core.iterDiffMem import mode1, mode3, DegException, breadth_first_search_diff_mem, test_print
from core.iter import tighten, tighten_iter
from core.log import Dumper
from uc.ucnet import DummyP, Exec, DummyAdv, FromA, FromZ, MesForP, MesForQ, Net, PidMes, SystemMes, ToF, ToP, UComp, UserMes, AdvMes
from uc.ucshell import LocalInd, PidAddr, Shell, cSystem
from ucauth.euf_cma_sign import GameSignReal, MemSignedKey, MemSignedSidKey
from ucauth.F_CA import F_CA, RetReq
from ucauth.F_auth import F_Auth
from ucauth.pauth import PAuth, PAuthMemInds, SidPid

from joblib import Memory
from ucauth.pauthx import SignLib, PAuthX

def printl(l):
  print('[')
  for t in l:
    print(str(t.args[0])+' ->\n'+str(t.args[1])+'\n')
#    print(str(t.args[0].groupID)+' ->\n'+str(t.args[1].groupID)+'\n')
  print(']')

def printlt(l):
  print('[')
  for t in l:
    print(str(t))
#    print(str(t.args[0].groupID)+' ->\n'+str(t.args[1].groupID)+'\n')
  print(']')

memory = Memory("./cachediruc3", verbose=0)

@memory.cache
def ctighten(f):
  return f.tighten()

#printl(F_CA)
F_CA = ctighten(F_CA)
print('F_CA tightened')
#printl(F_CA)

F_Auth = ctighten(F_Auth)
print('F_Auth tightened')
#printl(F_Auth)

GameSignReal = ctighten(GameSignReal)
print('GameSignReal tightened')
#printl(GameSignReal)

DummyAdv = ctighten(DummyAdv)
print('DummyAdv tightened')

Net = ctighten(Net)
print('Net tightened')

Exec = ctighten(Exec)
print('Exec tightened')

ShellReal = ctighten(Shell(PAuthMemInds))
print('Shell tightened')

#ShellF = ShellF.tighten()
#print('ShellF tightened')

PAuth = ctighten(PAuth)
print('PAuth tightened')

F_CA = F_CA#ShellF(F_CA).tighten()
F_Auth = ctighten(F_Auth)
print('F_CA and F_Auth shelled')

PShellAuth = ctighten(ShellReal(PAuth, no_tighten=True))
print('PAuth shelled')

NetReal = ctighten(Net(PShellAuth, F_CA, no_tighten=True))
print('Net shelled')
#printl(NetReal)
#Net(PAuth, F_CA, no_tighten=True)

T1 = ctighten(Exec(DummyAdv, no_tighten=True))
print('Exec 1 tighten')

RealModel = ctighten(T1(NetReal, no_tighten=True))
print('Real Model tighten')

print(len(RealModel))

PAuthX = ctighten(PAuthX)
PShellAuthX = ctighten(ShellReal(PAuthX, no_tighten=True))
print('PAuthX shelled')
#printl(PShellAuth)
#print(len(PShellAuthX), len(PShellAuth))

#breadth_first_search_diff_mem(
#  PShellAuth, PShellAuthX
#)

NetXReal = ctighten(Net(PShellAuthX, F_CA, no_tighten=True))
print('NetX shelled')
#Net(PAuth, F_CA, no_tighten=True)

RealModelX = ctighten(T1(NetXReal, no_tighten=True))
print('Real ModelX tighten')

RealModelXReal = ctighten(lib_call_to_comp(RealModelX, SignLib)(GameSignReal, no_tighten=True))
#RealModelXReal = RealModelX

print('Real ModelXReal tighten')
#s = Var('s')
#d = Var('d')
#y = Var('y')
#FailPattern = func(
#  StateMes(s, CallMes(Const("DEBUG"), c0)),
#  StateMes(d, OutMes(UpMes(y)))
#)

#printl(
#  [it for it in lib_call_to_comp(RealModelX, SignLib) if it.isIn(FailPattern)]
#)

#runOnSeq(RealModelXReal, [
#  OutMes(UserMes(PidMes(Var('a'), Var('b'), Const('AuthRegister')))),
#  CallMes(Mem(cortege(c0, cortege(c1, cortege(c0, cortege(c1, cortege(c0, Const('System'))))))), c0),
#  CallMes(Mem(cortege(c0, cortege(c1, cortege(c0, cortege(c1, cortege(c0, LocalInd(Const('MemReg')))))))), c0)
#])

print("---- SEARCH DIFF ---- "+ str(len(RealModel)) + ":" +str(len(RealModelXReal)))
z = Var('z')
v_pid = Var('pid')
v_sid = Var('sid')
v_pid2 = Var('pid2')
v_m = Var('m')
def check_message_sent(n, h, hf, is_last=False):
  printlt(hf)
  print(n.term().args[2].args[1])
  pass
try:
  partition = Partition([
    (["System"], v_pid),
    (["MemCAReg"], v_pid),
    (["MemCARet"], RetReq(v_pid, v_pid2)),
    (["MemCA"], v_pid),
    (["MemReg"], PidAddr(v_pid, c0)),
    (["MemRecv"], PidAddr(v_pid2, SidPid(v_sid, v_pid))),
    (["MemSend"], PidAddr(v_pid, v_sid)),
    (["MemKeyPair"], v_pid),
    (["MemSignedSid"], MemSignedSidKey(v_pid, v_sid)),
    (["MemSigned"], MemSignedKey(v_pid, v_sid, v_m)),
  ])
  if True:
    breadth_first_search_diff_mem(RealModel, RealModelXReal,
      cbk=Dumper("dumps/uc-auth-addsignlib.txt"),
#      cbk=check_message_sent,
      partition=partition
    )
  else:
    runOnSeq(RealModel, [])
except DegException as e:
  t_start =  e.start[0].term()
  h = e.start[1]
  mode = t_start.args[0]
  if mode==mode1:
    print('C1')
  else:
    print('C3')
#  runOnSeq(RealModelXReal if mode == mode1 else RealModel, e.call_history)
      
#  Exec(DummyAdv, Net(PAuth, F_CA)), 
#  Exec(DummyAdv, Net(PAuth, F_CA)),
#)
