from core.term import func, norm, Term, Func, Const, Var, termToStr
from core.notation import *
from core.iterProg import *
from uc.ucnet import FromA, FromP, FromZ, PidMes, SystemMes, ToF, UserMes

def callCbk2(ret, F, mes, cbk1, cbk2, debug=False):
  return lambda v: [
    Call(ret, F, UpMes(UpMes(mes))),
#    Call(c0, Const("DEBUGCBK1"), ret if debug else c0),
    Branches([
      [
        Parse(DownMes(v('inner')), ret),
        cbk1(v('inner')),
#        Call(c0, Const("DEBUGCBK1"), v('inner') if debug else c0),
        Call(ret, F, DownMes(v('inner'))),
        Back()
      ],
      [
        Parse(UpMes(DownMes(v('inner'))), ret),
#        Call(c0, Const("DEBUGCBK2"), v('inner') if debug else c0),
        cbk2(v('inner')),
        Call(ret, F, UpMes(DownMes(v('inner')))),
        Back()
      ],
      [
        Parse(UpMes(UpMes(ret)), ret)
      ]
    ])
  ]

cUser = Const('User')
cUserSid = Const('UserSid')
cSystem = ID(Const('System'))
cCorrupt = Const('Corrupt')

PStateMes = Func("PStateMes", 3)
PStateMesOut = Func("PStateMesOut", 2)

cGetPState = Const('GetPState')

ExtIdentity = Func('ExtIdentity', 2)

SPState = Func('SPState', 2)

LocalGetByAddr = Func('LocalGetByAddr', 2)
LocalSetByAddrValue = Func('LocalSetByAddrValue', 3)
LocalInd = Func('LocalInd', 1)
ExtKey = Func('ExtKey', 2)
PidAddr = Func('PidAddr', 2)
SidMes = Func('SidMes', 2)

def sendToP(locMems, Body, F, pid, sid, ret, mes, debug=False):
  return lambda v: [
#    Call(c0, Const("DEBUGSENDTOP"), c1 if debug else c0),
    callCbk2(
      ret, Body, mes, 
      lambda m: [
        Branches([
          [
            Parse(LocalGetByAddr(v('ind'), v('addr')), m),
            Branches(
              [[Test(v('ind'), locMemInd)] for locMemInd in locMems]
            ),
            Call(m, Mem(LocalInd(v('ind'))), GetByAddr(PidAddr(pid, v('addr')))),
          ],
          [
            Parse(LocalSetByAddrValue(v('ind'), v('addr'), v('val')), m),
            Branches(
              [[Test(v('ind'), locMemInd)] for locMemInd in locMems]
            ),
            Call(c0, Mem(LocalInd(v('ind'))), SetByAddrValue(PidAddr(pid, v('addr')), v('val'))),
            Set(m, c0)
          ]
        ])
      ],
      lambda m: [
#        Call(c0, Const("DEBUGSENDTOP"), FromP(PidMes(pid, sid, m)) if not debug else c0),
        Parse(SidMes(v('sidF'), v('mes')), m),
        Call(m, F, PidMes(pid, v('sidF'), v('mes')))
      ],
      debug=debug
    )
  ]

Shell = lambda locMems, debug: program(
  2,
  lambda v, Body, F: [
    Message(v("mes")),
    Branches([
      [
        Parse(FromZ(UserMes(PidMes(v('pid'), v('sid'), v('mes')))), v('mes')),
        Call(v('corrupted'), Mem(cSystem), GetByAddr(v('pid'))),
        Branches([
          [
            Test(v('corrupted'), cCorrupt),
            Return(c0)
          ],
          [
            Test(v('corrupted'), c0)
          ]
        ]),
        sendToP(
          locMems,              
          Body, F, v('pid'), v('sid'), v('mes'), 
          FromZ(PidMes(v('pid'), v('sid'), v('mes'))),
          debug=debug
        )
      ],
      [
        Parse(FromZ(SystemMes(PidMes(v('pid'), v('sid'), cCorrupt))), v('mes')),        
        #Call(c0, Mem(cSystem), SetByAddrValue(v('pid'), cCorrupt))
      ],
      [
        Parse(FromA(PidMes(v('pid'), v('sid'), v('mes'))), v('mes')),
        Call(v('corrupted'), Mem(cSystem), GetByAddr(v('pid'))),
        Branches([
          [
            Test(v('corrupted'), cCorrupt),
            Branches([
              [
                Test(v('mes'), LocalGetByAddr(v('ind'), v('addr'))),
                Call(v('data'), Mem(LocalInd(v('ind'))), GetByAddr(v('pid'))),
                Return(v('data'))
              ],
              [
                Parse(ToF(v('mes')), v('mes')),
                Call(v('mes'), F, FromP(PidMes(v('pid'), v('sid'), v('mes')))),
                Return(v('mes'))
              ]
            ])
          ],
          [
            Test(v('corrupted'), c0),
            sendToP(
              locMems,
              Body, F, v('pid'), v('sid'), v('mes'), 
              FromA(PidMes(v('pid'), v('sid'), v('mes')))
            )
          ]
        ]),
      ],
    ]),
    Return(v('mes'))
  ]
)

SystemToF = Func('SystemToF', 1)
AdvToCorrupted = Func('AdvToCorrupted', 1)
AdvToF = Func('AdvToF', 1)

ShellF = program(
  1,
  lambda v, F: [
    Message(v("mes")),
    Branches([
      [
        Parse(FromZ(SystemMes(PidMes(v('pid'), v('sid'), cCorrupt))), v('mes')),
        Call(c0, Mem(cSystem), SetByAddrValue(v('pid'), cCorrupt)),
        Return(c0)
      ], [
        Parse(FromZ(SystemMes(SystemToF(v('systemMes')))), v('mes')),
        Call(c0, F, FromZ(SystemMes(v('systemMes')))),
        Return(c0)
      ], [
        Parse(FromA(AdvToCorrupted(PidMes(v('pid'), v('sid'), v('mes')))), v('mes')),
        Call(v('corrupted'), Mem(cSystem), GetByAddr(v('pid'))),
        Branches([
          [
            Test(v('corrupted'), cCorrupt),
          ],
          [
            Test(v('corrupted'), c0),
            Return(c0)
          ]
        ]),
        Call(v('mes'), F, FromP(PidMes(v('pid'), v('sid'), v('mes')))),
        Return(v('mes'))
      ], [
        Parse(FromA(AdvToF(v('advMes'))), v('mes')),
        Call(v('mes'), F, FromA(v('advMes'))),
        Return(v('mes'))
      ], [
        Parse(FromP(v('pMes')), v('mes')),
        Call(v('mes'), F, FromP(v('pMes'))),
        Return(v('mes'))
      ]
    ])
  ]
)