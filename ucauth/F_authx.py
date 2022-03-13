from core.term import func, norm, Term, Func, Const, Var, termToStr
from core.notation import *
from core.iterProg import *
from ucauth.F_auth import AdvGetInfo, AdvGrant, AuthIdentity, MemAuth, MemAuthGrant, SendGet, SendGrantedInfo, SendReq, SendReqInfo, Sent
from ucauth.euf_cma_sign import ExtIdentity, GameSignedSid, MemSignedKey, MemSignedSidKey, MemSignedSidVal
from uc.ucnet import FromA, FromP, PidMes
from ucauth.pauthx import SignLib

F_AuthX = program(
  0,
  lambda v: [
    Message(v('mes')),
    Branches([
      [
        Parse(FromP(PidMes(v('pid'), v('sid'), SendReq(v('m')))), v('mes')),
        Call(v('mem'), Mem(MemAuth), GetByAddr(ExtIdentity(v('sid'), v('pid')))),
        Branches([
          [
            Test(v('mem'), c0),
          ], [
            Parse(SendReqInfo(v('m')), v('mem')),
            Return(c0)
          ]
        ]),
        Call(
          c0, Mem(MemAuth), 
          SetByAddrValue(ExtIdentity(v('sid'), v('pid')), SendReqInfo(v('m')))),
        Return(c0)
      ], [
        Parse(FromA(AdvGetInfo(v('sid'), v('pid'))), v('mes')),
        Call(v('mem'), Mem(MemAuth), GetByAddr(ExtIdentity(v('sid'), v('pid')))),
        Return(v('mem'))
      ], [
        Parse(FromA(AdvGrant(v('sid'), v('pid'), v('pid2'))), v('mes')),
        Call(v('mem'), SignLib, GameSignedSid(v('sid'), v('pid'))),
        Call(c0, Const("Debug"), v('mem')),
        Branches([
          [
            Parse(MemSignedSidVal(v('m')), v('mem')),
          ],
          [
            Test(v('mem'), c0),
            Return(c0)
          ]
        ]),
        Call(
          v('mem'), Mem(MemAuthGrant), 
          SetByAddrValue(AuthIdentity(v('sid'), v('pid'), v('pid2')), SendGrantedInfo(v('m')))
        ),
        Return(c0)
      ], [
        Parse(FromP(PidMes(v('pid2'), v('sid'), SendGet(v('pid')))), v('mes')),
        Call(
          v('memGrant'), Mem(MemAuthGrant), 
          GetByAddr(AuthIdentity(v('sid'), v('pid'), v('pid2')))),
        Branches([
          [
            Parse(SendGrantedInfo(v('m')), v('memGrant'))
          ], [
            Test(v('memGrant'), c0),
            Return(c0)
          ]
        ]),
        Return(Sent(v('m')))
      ]
    ])
  ]
)