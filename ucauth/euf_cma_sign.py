from core.term import func, norm, Term, Func, Const, Var, termToStr
from core.notation import *
from core.iterProg import *
from uc.ucshell import SidMes

SignKeyGen = Const('SignKeyGen')
SignKeyPair = Func('SignKeyPair', 2)

SignMakeSign = Const('SignMakeSign')
SignMakeSignArg = Func('SignMakeSignArg', 2)

SignVerify = Const('SignVerify')
SignedMes = Func('SignedMes', 2)
SignVerifyArgs = Func('SignVerifyArgs', 3)
VerifiedMes = Func('VerifiedMes', 1)

GameKeyGen = Func('GameKeyGen', 1)
GameSign = Func('GameSign', 3)
GameVerify = Func('GameVerify', 4)
GameSigned = Func('GameSigned', 3)
GameSignedSid = Func('GameSignedSid', 2)
GameCorrupt = Func('GameCorrupt', 1)

ExtIdentity = Func('ExtIdentity', 2)

MemSignCorrupted = ID(Const('MemSignCorrupted'))
MemKeyPair = ID(Const('MemKeyPair'))
MemSign = ID(Const('MemSign'))
MemSigned = ID(Const('MemSigned'))
MemSignedSid = ID(Const('MemSignedSid'))
MemSignedSidVal = Func("MemSignedSidVal", 1)

MemSignedKey = Func('MemSignedKey', 3)
MemSignedSidKey = Func('MemSignedSidKey', 2)

def getKeyPairByPid(pk, sk, pid):
  return lambda v: [
    Call(v('ret'), Mem(MemKeyPair), GetByAddr(pid)),
    Branches([
      [
        Test(v('ret'), c0),
        Call(v('ret'), SignKeyGen, c0),
        Call(c0, Mem(MemKeyPair), SetByAddrValue(pid, v('ret'))),
        Parse(SignKeyPair(pk, sk), v('ret'))
      ], [
        Parse(SignKeyPair(pk, sk), v('ret'))
      ]          
    ])
  ]

def getKeyPairByPidNoGen(pk, sk, pid):
  return lambda v: [
    Call(v('ret'), Mem(MemKeyPair), GetByAddr(pid)),
    Branches([
      [
        Test(v('ret'), c0),
        Return(c0)
      ], [
        Parse(SignKeyPair(pk, sk), v('ret'))
      ]          
    ])
  ]


GameSignBase = lambda ideal: program(
  0,
  lambda v: [
    Message(v('mes')),
    Branches([
      [
        Parse(GameKeyGen(v('pid')), v('mes')),
        getKeyPairByPid(v('pk'), v('sk'), v('pid')),
        Return(v('pk'))
      ],
      [
        Parse(GameSign(v('pid'), v('sid'), v('m')), v('mes')),
        getKeyPairByPidNoGen(v('pk'), v('sk'), v('pid')),
        Call(
          v('signed'), 
          Mem(MemSignedSid), 
          GetByAddr(
            MemSignedSidKey(v('pid'), v('sid')),
          )
        ),
        Branches([
          [
            Parse(MemSignedSidVal(v('t')), v('signed')),
            Return(c0)
          ], [
            Test(v('signed'), c0)
          ]
        ]),
        Call(v('sig'), SignMakeSign, SignMakeSignArg(v('sk'), SidMes(v('sid'), v('m')))),
        Call(
          c0, 
          Mem(MemSigned), 
          SetByAddrValue(
            MemSignedKey(v('pid'), v('sid'), v('m')),
            c1
          )
        ),
        Call(
          c0, 
          Mem(MemSignedSid), 
          SetByAddrValue(
            MemSignedSidKey(v('pid'), v('sid')),
            MemSignedSidVal(v('m'))
          )
        ),
        Return(v('sig'))
      ],
      [
        Parse(GameSignedSid(v('sid'), v('pid')), v('mes')),
        Call(
          v('signed'), 
          Mem(MemSignedSid), 
          GetByAddr(
            MemSignedSidKey(v('pid'), v('sid')),
          )
        ),
        Return(v('signed'))
      ],
      [
        Parse(GameVerify(v('pid'), v('sid'), v('m'), v('sig')), v('mes')),
        getKeyPairByPidNoGen(v('pk'), v('sk'), v('pid')),
        Call(v('ret'), SignVerify, SignVerifyArgs(SidMes(v('sid'), v('m')), v('pk'), v('sig'))),
        Branches([
          [
            Test(v('ret'), c0),
            Set(v('ret'), c0)
          ], [
            Test(v('ret'), c1),
            Set(v('ret'), VerifiedMes(v('m')))
          ]
        ]),
        Return(v('ret')) if not ideal else [
          Branches([
            [
              Test(v('ret'), VerifiedMes(v('m'))),
              Call(c0, Mem(MemSigned), SetByAddrValue(MemSignedKey(v('pid'), v('sid'), v('m')), c1)),
              Call(v('m'), Mem(MemSignedSid), GetByAddr(MemSignedSidKey(v('pid'), v('sid')))),
              Parse(MemSignedSidVal(v('m')), v('m')),
              Return(VerifiedMes(v('m')))
            ], [
              Test(v('ret'), c0),
              Return(c0)
            ]
          ])
        ]
      ]
    ])
  ]
)

GameSignIdeal = GameSignBase(True)
GameSignReal = GameSignBase(False)