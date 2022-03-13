from core.term import func, norm, Term, Func, Const, Var, termToStr
from core.notation import *
from core.iterProg import *

cP = Const("P")
cA = Const("A")
cZ = Const("Z")
cF = Const("F")

ToMes = Func("ToMes", 2)
FromMes = Func("FromMes", 2)

PidMes = Func("PidMes", 3)

SystemMes = Func("SystemMes", 1)
UserMes = Func("UserMes", 1)
AdvMes = Func("AdvMes", 1)

FromP = Func("FromP", 1)
FromA = Func("FromA", 1)
FromZ = Func("FromZ", 1)
FromF = Func("FromF", 1)
ToP = Func("ToP", 1)
ToF = Func("ToF", 1)
ToA = Func("ToA", 1)

def callCbk(ret, F, mes, cbk):
  return lambda v: [
    Call(ret, F, UpMes(mes)),
    Branches([
      [
        Parse(DownMes(v('inner')), ret),
        cbk(v('inner')),
        Call(ret, F, DownMes(v('inner'))),
        Back()
      ],
      [
        Parse(UpMes(ret), ret),
      ]
    ])
  ]


Exec = program(
  2,
  lambda v, A, Net: [
    Message(v('mes')),
#    Set(v('bug_original_input'), Func('DebugInputOriginal', 1)(v('mes'))),
    Branches([
      [
        Parse(UserMes(v('mes')), v('mes')),
        Call(v('mes'), Net, FromZ(UserMes(v('mes'))))
      ],
      [
        Parse(SystemMes(v('mes')), v('mes')),
        #TODO: Reenable corrupt
        #Stop(),
        Call(c0, Net, FromZ(SystemMes(v('mes')))),
        callCbk(v('ret'), A, SystemMes(v('mes')), lambda m: [
          Call(m, Net, FromA(m))
        ]),
        Test(v('ret'), c0),
        Set(v('mes'), c0)
      ],
      [
        Parse(AdvMes(v('mes')), v('mes')),
#        Set(v('bug_original'), Func('DebugAdvInput', 1)(v('mes'))),
        callCbk(v('mes'), A, AdvMes(v('mes')), lambda m: [
#          Set(v('bug_original'), Func('DebugOriginal2', 1)(m)),
          Call(m, Net, FromA(m))
        ])
      ]
    ]),
    Return(v('mes'))
  ]
)

DummyAdv = program(
  1,
  lambda v, Net: [
    Message(v('mes')),
    Branches([
    [
      Parse(SystemMes(v('mes')), v('mes')),
      Return(c0)
    ],
    [
      Parse(AdvMes(v('mes')), v('mes')),
      Call(v('mes'), Net, v('mes')),
      Return(v('mes'))
    ]
  ])]
)

Net = program(
  2,
  lambda v, P, F: [
    Message(v("mes")),
#    Set(v('bug_original'), Func('ExecSystemMes', 1)(v('mes'))),
    Branches([
      [
        Parse(FromZ(UserMes(v('mes'))), v('mes')),
        callCbk(v('mes'), P, FromZ(UserMes(v('mes'))), lambda m: [
          Call(m, F, FromP(m))
        ])
      ], [
        Parse(FromZ(SystemMes(v('mes'))), v('mes')),
        #TODO: Reenable corrupt
#        Stop(),
        callCbk(v('ret'), P, FromZ(SystemMes(v('mes'))), lambda m: Stop()),#Call(m, F, FromP(m))),
        Test(v('ret'), c0),
        Call(c0, F, FromZ(SystemMes(v('mes')))),
        Set(v('mes'), c0)
      ], [
        Parse(FromA(ToP(v('mes'))), v('mes')),
#        Call(c0, Const("Debug"), v("mes")),
        callCbk(v('mes'), P, FromA(v('mes')), lambda m: Call(m, F, FromP(m)))
      ], [
        Parse(FromA(ToF(v('mes'))), v('mes')),
        Call(v('mes'), F, FromA(v('mes')))
      ]
    ]),
    Return(v('mes'))
  ]
)

DummyP = program(
  1,
  lambda v, F: [
    Message(v("mes")),
    Branches([
      [
        Parse(FromZ(UserMes(v('mes'))), v('mes')),
        Call(v('mes'), F, v('mes')),
        Return(v('mes'))
      ],
      [
        Parse(FromZ(SystemMes(v('mes'))), v('mes')),
        Return(c0)
      ]
    ])
  ]
)

MesForP = Func('MesForP', 1)
MesForQ = Func('MesForQ', 1)

def ucCallQ(Q, H, mGet, mSend):
  return lambda v: [
    callCbk(mGet, Q, mSend, lambda mQ: Call(mQ, H, mQ))
  ]

def ucCallP(P, Q, H, mGet, mSend):
  return lambda v: [
    callCbk(mGet, P, mSend, lambda mP: ucCallQ(Q, H, mP, FromZ(UserMes(mP))))
  ]

UComp = program(
  3,
  lambda v, P, Q, H: [
    Message(v('mes')),
    Branches([
      [
        Parse(FromA(MesForP(v('mes'))), v('mes')),
        ucCallP(P, Q, H, v('mes'), FromA(v('mes')))
      ],
      [
        Parse(FromA(MesForQ(v('mes'))), v('mes')),
        ucCallQ(Q, H, v('mes'), FromA(v('mes')))
      ],
      [
        Parse(FromZ(UserMes(v('mes'))), v('mes')),
        ucCallP(P, Q, H, v('mes'), FromZ(UserMes(v('mes'))))
      ],
      [
        Parse(FromZ(SystemMes(v('mes'))), v('mes')),
        callCbk(v('ret'), P, FromZ(SystemMes(v('mes'))), lambda v: Stop()),
        Test(v('ret'), c0),
        callCbk(v('ret'), Q, FromZ(SystemMes(v('mes'))), lambda v: Stop()),
        Test(v('ret'), c0),
        Set(v('mes'), c0)
      ]
    ]),
    Return(v('mes'))
  ]
)