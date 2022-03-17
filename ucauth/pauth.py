from core.iterProgStandard import lib
from core.term import func, norm, Term, Func, Const, Var, termToStr
from core.notation import *
from core.iterProg import *
from ucauth.F_CA import RegisterReq, RegisteredVal, RetrieveGet, RetrieveReq, Retrieved
from ucauth.F_auth import AuthIdentity, AuthRegister, SendGet, SendReq, Sent
from ucauth.euf_cma_sign import ExtIdentity, SidMes, SignedMes, SignMakeSign, SignMakeSignArg, SignKeyGen, SignKeyPair, SignVerify, SignVerifyArgs, VerifiedMes
from uc.ucnet import FromA, FromP, FromZ, PidMes
from uc.ucshell import LocalGetByAddr, LocalSetByAddrValue, SidMes

Registered = Func('Registered', 1)

SStatePair = Func('SStatePair', 2)

GetSendReq = Const('GetSendReq')
TransmitSignedMes = Func('TransmitSignedMes', 3)
NotSignedMes = Func('NotSignedMes', 1)
AuthedMes = Func('AuthedMes', 1)

MemReg = ID(Const('MemReg'))
MemRecv = ID(Const('MemRecv'))
MemSend = ID(Const('MemSend'))

SidPid = Func('SidPid', 2)

PAuthMemInds = [MemReg, MemRecv, MemSend]

PAuth = program(
  2,
  lambda v, LocMem, F_CA: [
    Message(v('mes')),
    Branches([
      [
        Parse(FromA(PidMes(v('pid'), v('sid'), AuthRegister)), v('mes')),
        Call(v('pstate'), LocMem, LocalGetByAddr(MemReg, c0)),
        Branches([
          [
            Test(v('pstate'), c0)
          ], [
            Parse(Registered(v('x')), v('pstate')),
            Return(c0)
          ]
        ]),
        lib(v('keys'), SignKeyGen, c0),
        Parse(SignKeyPair(v('pk'), v('sk')), v('keys')),
        Call(v('x'), F_CA, SidMes(c0, RegisterReq(v('pk')))),
        Call(c0, LocMem, LocalSetByAddrValue(MemReg, c0, Registered(v('sk')))),
        Return(c0)
      ], [
        Parse(
          FromZ(
            PidMes(
              v('pid'), v('sid'), 
              SendReq(v('m'))
            )
          ), 
          v('mes')
        ),
        Call(v('mem'), LocMem, LocalGetByAddr(MemSend, v('sid'))),
        Branches([
          [
            Parse(NotSignedMes(v('mes')), v('mem')),
            Return(c0)
          ],
          [
            Parse(SignedMes(v('mes'), v('sign')), v('mem')),
            Return(c0)
          ],
          [
            Test(v('mem'), c0)
          ]
        ]),
        Call(c0, LocMem, LocalSetByAddrValue(MemSend, v('sid'), NotSignedMes(v('m')))),
        Return(c0)
      ], [
        Parse(
          FromA(
            PidMes(
              v('pid'), v('sid'), 
              GetSendReq
            )
          ), 
          v('mes')
        ),
        Call(v('send_state'), LocMem, LocalGetByAddr(MemSend, v('sid'))),
        Branches([
          [
            Parse(SignedMes(v('m'), v('sign')), v('send_state')),
          ], [
            Parse(NotSignedMes(v('m')), v('send_state')),
            Call(v('pstate'), LocMem, LocalGetByAddr(MemReg, c0)),
            Branches([
              [
                Parse(Registered(v('sk')), v('pstate')),
              ], [
                Test(v('pstate'), c0),
                Return(c0)
              ]
            ]),
            lib(v('sign'), SignMakeSign, SignMakeSignArg(v('sk'), SidMes(v('sid'), v('m')))),        
            Call(c0, LocMem, LocalSetByAddrValue(MemSend, v('sid'), SignedMes(v('m'), v('sign')))),
          ], [
            Test(v('send_state'), c0),
            Return(c0)
          ]
        ]),
        Return(SignedMes(v('m'), v('sign')))
      ], [
        Parse(
          FromA(
            PidMes(
              v('pid2'), v('sid'), 
              RetrieveReq(v('pid'))
            )
          ), 
          v('mes')
        ),
        Call(v('ca_val'), F_CA, SidMes(c0, RetrieveGet(v('pid')))),
        Call(c0, F_CA, SidMes(c0, RetrieveReq(v('pid')))),
        Return(c0)
      ], [
        Parse(
          FromA(
            PidMes(
              v('pid2'), v('sid'), 
              TransmitSignedMes(v('pid'), v('m'), v('sig'))
            )
          ), 
          v('mes')
        ),
        Call(v('ca_val'), F_CA, SidMes(c0, RetrieveGet(v('pid')))),
        Branches([
          [
            Test(v('ca_val'), c0),
            Return(c0)
          ], [
            Test(v('ca_val'), Retrieved(c0)),
            Return(c0)
          ], [
            Parse(Retrieved(RegisteredVal(v('pk'))), v('ca_val'))
          ]
        ]),
        lib(v('ver'), SignVerify, SignVerifyArgs(SidMes(v('sid'), v('m')), v('pk'), v('sig'))),
        Branches([
          [
            Test(v('ver'), c1)            
          ], [
            Test(v('ver'), c0),
            Return(c0)
          ]
        ]),
        Call(
          c0, LocMem, 
          LocalSetByAddrValue(MemRecv, SidPid(v('sid'), v('pid')), AuthedMes(v('m')))
        ),
        Return(VerifiedMes(v('m')))
      ], [
        Parse(
          FromZ(
            PidMes(
              v('pid2'), v('sid'), 
              SendGet(v('pid'))
            )
          ), 
          v('mes')
        ),
        Call(
          v('memAuth'), LocMem, 
          LocalGetByAddr(MemRecv, SidPid(v('sid'), v('pid')))
        ),
        Branches([
          [
            Parse(AuthedMes(v('m')), v('memAuth'))
          ], [
            Test(v('memAuth'), c0),
            Return(c0)
          ]
        ]),
        Return(Sent(v('m')))
      ]
    ])
  ]
)