from core.iterDebug import runOnSeq
from core.iterProgStandard import callCbk
from core.term import func, norm, Term, Func, Const, Var, termToStr
from core.notation import *
from core.iterAlgebra import comp, IterItem, iter_var
from core.iterProg import *
from core.iterDiffMem import DegException, breadth_first_search_diff_mem, test_print
from core.iter import tighten, tighten_iter
from uc.ucnet import DummyP, Exec, DummyAdv, FromA, FromZ, MesForP, MesForQ, Net, SystemMes, ToF, ToP, UComp, UserMes, AdvMes

def printl(l):
  print('[')
  for t in l:
    print(str(t.args[0])+' ->\n'+str(t.args[1])+'\n')
  print(']')

def callPT1(P, Exec, mGet, mSend):
  return lambda v: [
    callCbk(mGet, P, mSend, lambda mP: Call(
      mP, Exec, UserMes(mP)
    ))
  ]

T1 = program(
  2,
  lambda v, P, Exec: [
    Message(v('mes')),
    Branches([
      [
        Parse(UserMes(v('mes')), v('mes')),
        callPT1(P, Exec, v('mes'), FromZ(UserMes(v('mes'))))
      ],
      [
        Parse(SystemMes(v('mes')), v('mes')),
        callCbk(v('ret'), P, FromZ(SystemMes(v('mes'))), lambda m: Stop()),
        Test(v('ret'), c0),
        Call(c0, Exec, SystemMes(v('mes'))),
        Set(v('mes'), c0)
      ],
      [
        Parse(AdvMes(ToP(MesForP(v('mes')))), v('mes')),
        callPT1(P, Exec, v('mes'), FromA(v('mes')))
      ],
      [
        Parse(AdvMes(ToP(MesForQ(v('mes')))), v('mes')),
        Call(v('mes'), Exec, AdvMes(ToP(v('mes'))))
      ],
      [
        Parse(AdvMes(ToF(v('mes'))), v('mes')),
        Call(v('mes'), Exec, AdvMes(ToF(v('mes'))))
      ]
    ]),
    Return(v('mes'))
  ]
)

def callSQT2(SQ, Exec, mGet, mSend):
  return lambda v: [
    callCbk(mGet, SQ, mSend, lambda mSQ: [
      Parse(ToF(mSQ), mSQ),
      Call(
        mSQ, Exec, AdvMes(ToF(mSQ))
      )
    ])
  ]

T2 = program(
  2,
  lambda v, SQ, Exec: [
    Message(v('mes')),
    Branches([
      [
        Parse(UserMes(v('mes')), v('mes')),
        Call(v('mes'), Exec, UserMes(v('mes')))
      ],
      [
        Parse(SystemMes(v('mes')), v('mes')),
        Call(c0, Exec, SystemMes(v('mes'))),
        callSQT2(SQ, Exec, v('ret'), SystemMes(v('mes'))),
        Test(v('ret'), c0),
        Set(v('mes'), c0)
      ],
      [
        Parse(AdvMes(ToP(MesForP(v('mes')))), v('mes')),
        Call(v('mes'), Exec, AdvMes(ToP(v('mes')))),
      ],
      [
        Parse(AdvMes(ToP(MesForQ(v('mes')))), v('mes')),
        callSQT2(SQ, Exec, v('mes'), AdvMes(ToP(v('mes'))))
      ],
      [
        Parse(AdvMes(ToF(v('mes'))), v('mes')),
        callSQT2(SQ, Exec, v('mes'), AdvMes(ToF(v('mes'))))
      ]
    ]),
    Return(v('mes'))
  ]
)

def callSP_SPQ(SP, Net, mGet, mSend):
  return lambda v: [
    callCbk(mGet, SP, mSend, lambda mSP: [
      Parse(ToF(mSP), mSP),
      Call(
        mSP, Net, ToF(mSP)
      )
    ])
  ]

def callSQ_SPQ(SP, SQ, Net, mGet, mSend):
  return lambda v: [
    callCbk(mGet, SQ, mSend, lambda mSQ: [
      Parse(ToF(mSQ), mSQ),
      callSP_SPQ(SP, Net, mSQ, AdvMes(ToF(mSQ)))
    ])
  ]

SPQ = program(
  3,
  lambda v, SP, SQ, Net: [
    Message(v('mes')),
    Branches([
      [
        Parse(SystemMes(v('mes')), v('mes')),
        callSP_SPQ(SP, Net, v('ret'), SystemMes(v('mes'))),
        Test(v('ret'), c0),
        callSQ_SPQ(SP, SQ, Net, v('ret'), SystemMes(v('mes'))),
        Test(v('ret'), c0),
        Set(v('mes'), c0)
      ],
      [
        Parse(AdvMes(ToP(MesForP(v('mes')))), v('mes')),
        callSP_SPQ(SP, Net, v('mes'), AdvMes(ToP(v('mes')))),
      ],
      [
        Parse(AdvMes(ToP(MesForQ(v('mes')))), v('mes')),
        callSQ_SPQ(SP, SQ, Net, v('mes'), AdvMes(ToP(v('mes')))),
      ],
      [
        Parse(AdvMes(ToF(v('mes'))), v('mes')),
        callSQ_SPQ(SP, SQ, Net, v('mes'), AdvMes(ToF(v('mes')))),
      ]
    ]),
    Return(v('mes'))
  ]
)

Z = iter_var('Z')
A = iter_var('A')
N = iter_var('N')
F = iter_var('F')
G = iter_var('G')
H = iter_var('H')
P = iter_var('P')
Q = iter_var('Q')
SP = iter_var('SP')
SQ = iter_var('SQ')


T1 = T1.tighten()
T2 = T2.tighten()
SPQ = SPQ.tighten()
Exec = Exec.tighten()
Net = Net.tighten()
UComp = UComp.tighten()
DummyAdv = DummyAdv.tighten()

breadth_first_search_diff_mem(
  Exec(DummyAdv, Net(UComp(P, Q), H)), 
  T1(P)(Exec(DummyAdv, Net(Q, H)))
)

breadth_first_search_diff_mem(
  T1(P)(Exec(SQ, Net(DummyP, G))),
  T2(SQ)(Exec(DummyAdv, Net(P, G)))
)

breadth_first_search_diff_mem(
  T2(SQ)(Exec(SP, Net(DummyP, F))),
  Exec(SPQ(SP, SQ), Net(DummyP, F))
)
