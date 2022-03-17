from core.iterProgStandard import callCbk2, lib, mem
from core.term import func, norm, Term, Func, Const, Var, termToStr
from core.notation import *
from core.iterProg import *
from uc.ucnet import FromA, FromP, FromZ, PidMes, SystemMes, ToF, UserMes

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

def sendToP(locMems, Body, F, pid, sid, ret, mes):
  return lambda v: [
    callCbk2(
      ret, Body, mes, 
      lambda m: [
        Branches([
          [
            Parse(LocalGetByAddr(v('ind'), v('addr')), m),
            Branches(
              [[Test(v('ind'), locMemInd)] for locMemInd in locMems]
            ),
            mem(m, LocalInd(v('ind')), GetByAddr(PidAddr(pid, v('addr')))),
          ],
          [
            Parse(LocalSetByAddrValue(v('ind'), v('addr'), v('val')), m),
            Branches(
              [[Test(v('ind'), locMemInd)] for locMemInd in locMems]
            ),
            mem(c0, LocalInd(v('ind')), SetByAddrValue(PidAddr(pid, v('addr')), v('val'))),
            Set(m, c0)
          ]
        ])
      ],
      lambda m: [
#        Call(c0, Const("DEBUGSENDTOP"), FromP(PidMes(pid, sid, m)) if not debug else c0),
        Parse(SidMes(v('sidF'), v('mes')), m),
        Call(m, F, PidMes(pid, v('sidF'), v('mes')))
      ]
    )
  ]

Shell = lambda locMems: program(
  2,
  lambda v, Body, F: [
    Message(v("mes")),
    Branches([
      [
        Parse(FromZ(UserMes(PidMes(v('pid'), v('sid'), v('mes')))), v('mes')),
        mem(v('corrupted'), cSystem, GetByAddr(v('pid'))),
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
          FromZ(PidMes(v('pid'), v('sid'), v('mes')))
        )
      ],
      [
        Parse(FromZ(SystemMes(PidMes(v('pid'), v('sid'), cCorrupt))), v('mes')),        
        #TODO: Reenable corrupt
        #Call(c0, Mem(cSystem), SetByAddrValue(v('pid'), cCorrupt))
      ],
      [
        Parse(FromA(PidMes(v('pid'), v('sid'), v('mes'))), v('mes')),
        mem(v('corrupted'), cSystem, GetByAddr(v('pid'))),
        Branches([
          [
            Test(v('corrupted'), cCorrupt),
            Branches([
              [
                Test(v('mes'), LocalGetByAddr(v('ind'), v('addr'))),
                mem(v('data'), LocalInd(v('ind')), GetByAddr(v('pid'))),
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