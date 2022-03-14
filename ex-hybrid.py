from core.iterMap2 import Partition
from core.term import func, norm, Term, Func, Const, Var, termToStr
from core.notation import *
from core.iterAlgebra import comp, IterItem, iter_var
from core.iterEq import automaton_diff, print_diff, backtrace_func_diff
from core.iterExpr import automaton_expression
from core.iterProg import *
from core.iterDiffMem import breadth_first_search_diff_mem, test_print
from core.iter import tighten, tighten_iter

lk = Var('lk')
rk = Var('rk')
lv = Var('lv')
rv = Var('rv')
lc = Var('lc')
rc = Var('rc')
lx = Var('lx')
rx = Var('rx')
s = Var('s')
d = Var('d')
x = Var('x')
y = Var('y')
X = iter_var('X')
Y = iter_var('Y')
Z = iter_var('Z')
mes = Var('mes')
mesA = Var('mesA')
mesAB = Var('mesAB')
mesBA = Var('mesBA')
ret = Var('ret')

AddrMes = Func('AddrMes', 2)
addr = Var('addr')

I = automaton_expression(1)
Comp = automaton_expression((1, 2))

a = Var('a')
bx = Var('bx')
b = Var('b')
d = Var('d')
MemOnce = Const('MemOnce')

sMA = Var('sMA')
c2 = cN(2)

SetAddr = Func('SetAddr', 1)
GetFirst = Func('GetFirst', 1)

def check(r, h):
#  print(h[-1].args[1])
  print(r.t)
#  printl(h)

#breadth_first_search_diff_mem(Comp, I(Comp), check)
Fixed = Func('Fixed', 1)

def memOnce(b, ind, addr, val):
  return lambda v: Block([
    Call(v('cur_mem'), Mem(ind), GetByAddr(addr)),
    Branches([
      [
        Test(v('cur_mem'), c0),
        Set(b, val),
        Call(c0, Mem(ind), SetByAddrValue(addr, Fixed(val)))
      ],
      [
        Parse(Fixed(v('cur_mem')), v('cur_mem')),
        Set(b, v('cur_mem'))        
      ]
    ])
  ])

def accBitDelta(b, d, fr = None):
  if fr is None: fr = b
  return lambda v: [Branches([
    [
      Test([fr, v('bOld')], [c0, c0]),
      Set(d, c0),
      Set(b, c0)
    ],
    [
      Test([fr, v('bOld')], [c0, c1]),
      Set(d, c0),
      Set(b, c1)
    ],
    [
      Test([fr, v('bOld')], [c1, c0]),
      Set(d, c1),
      Set(v('bOld'), c1),
      Set(b, c1)
    ],
    [
      Test([fr, v('bOld')], [c1, c1]),
      Set(d, c0),
      Set(b, c1)
    ],
  ]), Set(v('d1'), Func("DebugAcc")(v('bOld')))]

def accBit(b):
  return lambda v: accBitDelta(b, v('d'))

ButOne = program(
  3,
  lambda v, MA, A, X: [
    Message(AddrMes(v('addr'), v('a'))),
    Call(v('b'), X, c0),
    accBitDelta(v('b'), v('d')),
    memOnce(v('d'), c0, v('addr'), v('d')),
#    Set(v('d'), c0),
    Branches([
      [
        Test(v('d'), c0),
        Call(v('ret'), MA, AddrMes(v('addr'), v('a'))),
      ],
      [
        Test(v('d'), c1),
        Call(v('ret'), A, v('a'))
      ]
    ]),
    Return(v('ret'))
  ]
)

HybridM = program(
  3,
  lambda v, MA, MB, X: [
    Message(AddrMes(v('addr'), v('a'))),
    Call(v('b'), X, c0),
    accBit(v('b')),
    memOnce(v('b'), c0, v('addr'), v('b')),
    Branches([
      [
        Test(v('b'), c0),
        Call(v('ret'), MA, AddrMes(v('addr'), v('a'))),
      ],
      [
        Test(v('b'), c1),
        Call(v('ret'), MB, AddrMes(v('addr'), v('a')))
      ]
    ]),
    Return(v('ret'))
  ]
)

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

HybridM05 = program(
  3,
  lambda v, MA, MB, X: [
    Message(AddrMes(v('addr'), v('a'))),
    Call(v('b'), X, c0),
    accBitDelta(v('b'), v('d')),
    memOnce(v('b'), c0, v('addr'), v('b')),
    Branches([
      [
        Test(v('b'), c0),
        Call(v('ret'), MA, AddrMes(v('addr'), v('a')))
      ],
      [
        Test(v('b'), c1),
        Call(v('ret'), MB, AddrMes(v('addr'), v('a')))
      ]
    ]),
    Return(v('ret'))
  ]
)

HybridM1 = program(
  3,
  lambda v, MA, MB, X: [
    Message(AddrMes(v('addr'), v('a'))),
    Call(v('b'), X, c0),
    accBitDelta(v('b'), v('d')),
    memOnce(v('b'), c0, v('addr'), v('b')),
    Branches([
      [
        Test(v('b'), c0),
        Call(v('ret'), MA, AddrMes(v('addr'), v('a')))
      ],
      [
        Test(v('b'), c1),
        callCbk(v('ret'), MB, AddrMes(v('addr'), v('a')), lambda b: [Set(b, v('d'))]),
      ]
    ]),
    Return(v('ret'))
  ]
)

HybridM2 = program(
  4,
  lambda v, MA, MB, A, X: [
    Message(AddrMes(v('addr'), v('a'))),
    Call(v('b'), X, c0),
    accBitDelta(v('b'), v('d')),
    memOnce(v('b'), c0, v('addr'), v('b')),
    memOnce(v('d'), c1, v('addr'), v('d')),
    Branches([
      [
        Test(v('b'), c0),
        Branches([
          [
            Test(v('d'), c0),
            Call(v('ret'), MA, AddrMes(v('addr'), v('a')))
          ],
          [
            Test(v('d'), c1),
            Call(v('ret'), A, v('a'))            
          ]
        ]),
      ],
      [
        Test(v('b'), c1),
        Call(v('ret'), MB, AddrMes(v('addr'), v('a')))
      ]
    ]),
    Return(v('ret'))
  ]
)

HybridM3 = program(
  3,
  lambda v, MA, MB, X: [
    Message(AddrMes(v('addr'), v('a'))),
    Call(v('b'), X, c0),
    accBitDelta(v('b'), v('d')),
    memOnce(v('b'), c0, v('addr'), v('b')),
    memOnce(v('d'), c1, v('addr'), v('d')),
    Branches([
      [
        Test(v('b'), c0),
        Call(v('ret'), MA, AddrMes(v('addr'), v('a')))
      ],
      [
        Test(v('b'), c1),
        Branches([
          [
            Test(v('d'), c0),
            Call(v('ret'), MB, AddrMes(v('addr'), v('a')))
          ],
          [
            Test(v('d'), c1),
            Call(v('ret'), MA, AddrMes(v('addr'), v('a')))
#            Call(v('ret'), A, v('a'))            
          ]
        ]),
      ]
    ]),
    Return(v('ret'))
  ]
)


HybridM4 = program(
  3,
  lambda v, MA, MB, X: [
    Message(AddrMes(v('addr'), v('a'))),
    Call(v('b'), X, c0),
    accBitDelta(v('b'), v('d')),
    memOnce(v('b'), c0, v('addr'), v('b')),
    Branches([
      [
        Test(v('b'), c0),
        Call(v('ret'), MA, AddrMes(v('addr'), v('a')))
      ],
      [
        Test(v('b'), c1),
        callCbk(v('ret'), MB, AddrMes(v('addr'), v('a')), lambda b: [Set(b, v('d'))]),
      ]
    ]),
    Return(v('ret'))
  ]
)

HybridM5 = program(
  3,
  lambda v, MA, MB, X: [
    Message(AddrMes(v('addr'), v('a'))),
    Call(v('b'), X, c0),
    accBitDelta(v('b'), v('d')),
    memOnce(v('b'), c0, v('addr'), v('b')),
    memOnce(v('d'), c1, v('addr'), v('d')),
    Branches([
      [
        Test(v('b'), c0),
        callCbk(v('ret'), MA, AddrMes(v('addr'), v('a')), lambda b: [Set(b, c0)]),
      ],
      [
        Test(v('b'), c1),
        Branches([
          [
            Test(v('d'), c0),
            Call(v('ret'), MB, AddrMes(v('addr'), v('a')))
          ],
          [
            Test(v('d'), c1),
            callCbk(v('ret'), MA, AddrMes(v('addr'), v('a')), lambda b: [Set(b, c1)]),
#            Call(v('ret'), A, v('a'))            
          ]
        ]),
      ]
    ]),
    Return(v('ret'))
  ]
)

C0 = program(
  0,
  lambda v: [Return(c0)]
)

C1 = program(
  0,
  lambda v: [Return(c1)]
)

TestP = program(
  0,
  lambda v: [
    Message(v('addr')),
    memOnce(v('b'), c0, v('addr'), c1),
    memOnce(v('b'), c0, v('addr'), c2),
    Return(v('b'))
  ]
)

TestP1 = program(
  0,
  lambda v: [Return(c1)]
)

MInterface = IterItem([
  func(StateMes(c0, OutMes(UpMes(AddrMes(a, x)))), StateMes(c1, OutMes(DownMes(AddrMes(a, x))))),
  func(StateMes(c1, OutMes(DownMes(a))), StateMes(c0, OutMes(UpMes(a))))
])
 
OneInterface = IterItem([
  func(StateMes(c0, OutMes(UpMes(AddrMes(a, x)))), StateMes(c1, OutMes(DownMes(x)))),
  func(StateMes(c1, OutMes(DownMes(a))), StateMes(c0, OutMes(UpMes(a))))
])

MImitate = program(
  2,
  lambda v, MA, X: [
    Message(AddrMes(v('addr'), v('a'))),
    Call(v('b'), X, c0),
    Call(v('ret'), MA, AddrMes(v('addr'), v('a'))),
    Return(v('ret'))
  ]
)

Shift = program(
  2,
  lambda v, A, X: [    
    Message(v('mes')),
    Call(v('mesA'), A, UpMes(v('mes'))),
    Branches([
      [
        Parse(DownMes(v('mesAB')), mesA),
        Call(v('mesBA'), X, v('mesAB')),
        accBitDelta(v('b'), v('d'), v('mesBA')),
        Branches([
          [Test(v('d'), c1), Set(v('b'), c0)],
          [Test(v('d'), c0)]
        ]),
        Set(v('d1'), Func("DebugD")(v('d'))),
        Set(v('d2'), Func("DebugShift")(v('b'))),
        Call(mesA, A, DownMes(v('b'))),
        Back()
      ],
      [
        Parse(UpMes(v('mes')), v('mesA')),
        Return(v('mes'))
      ]
    ])
  ], print_desc=True
)


 
#printl(Test)
#printl(ButOne(X, Y, C0).tighten())

MInterface = MInterface.tighten()

MX = MInterface(X)
MY = MInterface(Y)

HybridM = HybridM.tighten()
HybridM1 = HybridM1.tighten()
#HybridM3 = HybridM3.tighten()
#HybridM5 = HybridM5.tighten()
MImitate = MImitate.tighten()
#ButOne = ButOne.tighten()
#Shift = Shift.tighten()

#printl(HybridM05)
#breadth_first_search_diff_mem(ButOne(MX, Y, C0), MImitate(MX, C0))
#breadth_first_search_diff_mem(HybridM(MX, MY, C0), MX)
#breadth_first_search_diff_mem(HybridM, HybridM, test_print)
#breadth_first_search_diff_mem(HybridM, HybridM05, test_print)
# *
breadth_first_search_diff_mem(HybridM(MX, MY), HybridM1(MX, MImitate(MY)), partition=Partition([
  (["0"], x), (["1"], x)
]))
#breadth_first_search_diff_mem(HybridM1(ButOne(MX, Z), MY), HybridM2(MX, MY, Z))
#breadth_first_search_diff_mem(HybridM4(MX, MImitate(MY)), HybridM(MX, MY))
# *
#breadth_first_search_diff_mem(Shift(HybridM(MX, MY)), HybridM3(MX, MY))
#breadth_first_search_diff_mem(Shift(HybridM(MX, MY)), HybridM5(MImitate(MX), MY))
# *
#breadth_first_search_diff_mem(HybridM3(MX, MY), HybridM5(MImitate(MX), MY))

#t0 = HybridM1.tighten()
#print("t0")
#ButOne = ButOne.tighten()
#print("tButOne")
#tButOneMXZ = ButOne(MX, Z).tighten()
#print("tButOneMXZ")
#t1 = t0(tButOneMXZ, MY).tighten()
#print("t1 done")
#tButOneMYZ = ButOne(MY, Z).tighten()
#tM5 = HybridM5.tighten()
#t2 = tighten_iter(tM5(MX, tButOneMYZ))


#print("t1 done")
#print("pretighten done")
# *
#breadth_first_search_diff_mem(HybridM1(MX, ButOne(MY, Z)), HybridM5(ButOne(MX, Z), MY))

#breadth_first_search_diff_mem(
#  program(0, lambda v: [Message(v('b')), accBit(v('b')), Return(v('b'))]), 
#  program(0, lambda v: [Message(v('b')), accBitDelta(v('b'), v('d')), Return(v('b'))])
#)

#HybridM

#printl(ButOne)
#printl(ReplaceOne.tighten(include_all=True))
#printl(ButOne.tighten())

#print_diff(automaton_diff(Comp(X, Y), Comp2.build()(X, Y)))
#print_diff(automaton_diff(I, I))
