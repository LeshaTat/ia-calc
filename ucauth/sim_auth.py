from core.term import func, norm, Term, Func, Const, Var, termToStr
from core.notation import *
from core.iterProg import *
from uc.ucshell import PStateMes
from ucauth.F_CA import AdvRegisterGrant, AdvRetrieveGrant, RetrieveReq
from ucauth.F_auth import AdvGetInfo, AdvGrant, AuthInfo, AuthRegister, SendGet, SendReq, SendReqInfo, Sent
from ucauth.euf_cma_sign import ExtIdentity, MemSignedKey, VerifiedMes
from uc.ucnet import AdvMes, FromA, FromP, FromZ, PidMes, ToF, ToP, UserMes
from ucauth.pauth import GetSendReq, TransmitSignedMes

SimAuth = program(
  2,
  lambda v, SimNet, Net: [
    Message(v('mes')),
    Branches([
      [
        Parse(AdvMes(ToP(
            PidMes(
              v('pid'), v('sid'), AuthRegister
            )
          )), 
          v('mes')
        ),
        Call(v('ret'), SimNet, FromA(
          ToP(PidMes(v('pid'), v('sid'), AuthRegister))
        )),
        Return(v('ret'))
      ], [
        Parse(AdvMes(ToP(
            PidMes(
              v('pid'), v('sid'), GetSendReq
            )
          )), 
          v('mes')
        ),
        Call(
          v('info'), 
          Net, 
          ToF(AdvGetInfo(v('sid'), v('pid')))
        ),
#        Call(c0, Const("Debug"), v('info')),
        Branches([
          [
            Test(v('info'), c0)
          ],
          [
            Parse(SendReqInfo(v('m')), v('info')),
            Call(v('t'), SimNet, FromZ(
              UserMes(PidMes(v('pid'), v('sid'), SendReq(v('m'))))
            )),
#            Call(c0, Const("Debug"), c0)
          ]
        ]),
        Call(v('ret'), SimNet, FromA(
          ToP(PidMes(v('pid'), v('sid'), GetSendReq))
        )),
        Return(v('ret'))
      ],
      [
        Parse(AdvMes(ToP(
            PidMes(
              v('pid2'), v('sid'), RetrieveReq(v('pid'))
            )
          )), 
          v('mes')
        ),
        Call(v('ret'), SimNet, FromA(
          ToP(PidMes(v('pid2'), v('sid'), RetrieveReq(v('pid'))))
        )),
        Return(c0)
      ],
      [
        Parse(AdvMes(ToP(
            PidMes(
              v('pid2'), v('sid'), TransmitSignedMes(v('pid'), v('m'), v('sig'))
            )
          )), 
          v('mes')
        ),
        Call(v('ret'), SimNet, FromA(
          ToP(PidMes(v('pid2'), v('sid'), TransmitSignedMes(v('pid'), v('m'), v('sig'))))
        )),
#        Call(c0, Const('Debug'), Sent(v('ret'))),
        Branches([
          [
            Test(v('ret'), c0),
            Return(c0)
          ], [
            Parse(VerifiedMes(v('m')), v('ret')),
            Call(
              v('info'), 
              Net, 
              ToF(AdvGrant(v('sid'), v('pid'), v('pid2')))
            ),
            Return(v('ret'))
          ]
        ]),
        Return(v('ret'))
      ],
      [
        Parse(AdvMes(ToF(
            AdvRegisterGrant(v('pid'))
          )), 
          v('mes')
        ),
        Call(v('ret'), SimNet, FromA(
          ToF(AdvRegisterGrant(v('pid')))
        )),
        Return(v('ret'))
      ],
      [
        Parse(AdvMes(ToF(
            AdvRetrieveGrant(v('pid'), v('pid2'))
          )), 
          v('mes')
        ),
        Call(v('ret'), SimNet, FromA(
          ToF(AdvRetrieveGrant(v('pid'), v('pid2')))
        )),
        Return(v('ret'))
      ]
   ])
  ]
)