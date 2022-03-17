from core.iterProgStandard import mem
from core.term import func, norm, Term, Func, Const, Var, termToStr, ID
from core.notation import *
from core.iterProg import *
from uc.ucnet import FromA, FromP, PidMes

RegisterReq = Func('RegisterReq', 1)
RetrieveReq = Func('RetrieveReq', 1)
RetrieveGet = Func('RetrieveGet', 1)
Retrieved = Func('Retrieved', 1)

AdvGetInfo = Func('AdvGetInfo', 2)
AdvRegisterGrant = Func('AdvRegisterGrant', 1)
AdvRetrieveGrant = Func('AdvRetrieveGrant', 2)

AdvCAInfo = Func('AdvCAInfo', 3)

MemCA = ID(Const('MemCA'))
MemCAReg = ID(Const('MemCAReg'))
MemCARet = ID(Const('MemCARet'))

RegReq = Func('RegReq', 1)

Registered = Const('Registered')

RetrieveRequested = Const('RetrieveRequested')
RetrieveGranted = Const('RetrieveGranted')

RegisteredVal = Func('RegisteredVal', 1)

RetReq = Func('RetReq', 2)

RegSid = Const('RegSid')

F_CA = program(
  0,
  lambda v: [
    Message(v('mes')),
    Branches([
      [
        Parse(FromP(PidMes(v('pid'), c0, RegisterReq(v('v')))), v('mes')),
        mem(v('memReg'), MemCAReg, GetByAddr(v('pid'))),
        Branches([
          [
            Test(v('memReg'), c0),
            mem(c0, MemCAReg, SetByAddrValue(v('pid'), RegReq(v('v')))),
            Return(c0)
          ], [
            Parse(RegReq(v('x')), v('memReg')),
            Return(c0)
          ], [
            Test(v('memReg'), Registered),
            Return(c0)
          ]
        ]),
      ],
      [
        Parse(FromA(AdvRegisterGrant(v('pid'))), v('mes')),
        mem(v('mem'), MemCAReg, GetByAddr(v('pid'))),
        Branches([
          [
            Parse(RegReq(v('v')), v('mem')),
            mem(c0, MemCA, SetByAddrValue(v('pid'), RegisteredVal(v('v')))),
            mem(c0, MemCAReg, SetByAddrValue(v('pid'), Registered)),
            Return(c0)
          ],
          [
            Test(v('mem'), c0),
            Return(c0)
          ], [
            Test(v('mem'), Registered),
            Return(c0)
          ]
        ]),
      ],
      [
        Parse(FromP(PidMes(v('pid'), c0, RetrieveReq(v('pid2')))), v('mes')),
        mem(v('memRet'), MemCARet, GetByAddr(RetReq(v('pid'), v('pid2')))),
        Branches([
          [
            Test(v('memRet'), c0),
            mem(c0, MemCARet, SetByAddrValue(RetReq(v('pid'), v('pid2')), RetrieveRequested)),
            Return(c0)
          ], [
            Test(v('memRet'), RetrieveRequested),
            Return(c0)
          ], [
            Test(v('memRet'), RetrieveGranted),
            Return(c0)
          ]
        ]),
      ], 
#      [
#        Parse(FromA(AdvGetInfo(v('pid'), v('pid2'))), v('mes')),
#        Call(v('memReg'), Mem(MemCAReg), GetByAddr(v('pid'))),
#        Call(v('memRet'), Mem(MemCARet), GetByAddr(RetReq(v('pid'), v('pid2')))),
#        Call(v('mem'), Mem(MemCA), GetByAddr(v('pid'))),
#        Return(AdvCAInfo(v('mem'), v('memReg'), v('memRet')))
#      ], 
      [
        Parse(FromA(AdvRetrieveGrant(v('pid'), v('pid2'))), v('mes')),
        mem(v('memRet'), MemCARet, GetByAddr(RetReq(v('pid'), v('pid2')))),
        Branches([
          [
            Test(v('memRet'), RetrieveRequested),
            mem(c0, MemCARet, SetByAddrValue(RetReq(v('pid'), v('pid2')), RetrieveGranted)),
            Return(c0)
          ], [
            Test(v('memRet'), RetrieveGranted),
            Return(c0)
          ], [
            Test(v('memRet'), c0),
            Return(c0)
          ]
        ]),
      ], 
      [
        Parse(FromP(PidMes(v('pid'), c0, RetrieveGet(v('pid2')))), v('mes')),
        mem(v('memRet'), MemCARet, GetByAddr(RetReq(v('pid'), v('pid2')))),
        Branches([
          [
            Parse(RetrieveGranted, v('memRet')),
            mem(v('mem'), MemCA, GetByAddr(v('pid2'))),
            Return(Retrieved(v('mem')))
          ], [
            Parse(RetrieveRequested, v('memRet')),
            Return(c0)
          ], [
            Test(v('memRet'), c0),
            Return(c0)
          ]
        ])
      ]
    ])
  ]
)
