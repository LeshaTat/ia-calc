from core.iterMap2 import Partition
from core.iterProgStandard import callCbk, mem
from core.log import Dumper, printl
from core.term import func, norm, Term, Func, Const, Var, termToStr
from core.notation import *
from core.iterAlgebra import comp, IterItem, iter_var
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

a = Var('a')
bx = Var('bx')
b = Var('b')
d = Var('d')
MemOnce = Const('MemOnce')

sMA = Var('sMA')
c2 = cN(2)

SetAddr = Func('SetAddr', 1)
GetFirst = Func('GetFirst', 1)

Fixed = Func('Fixed', 1)

def memOnce(b, ind, addr, val):
  return lambda v: Block([
    mem(v('cur_mem'), ind, GetByAddr(addr)),
    Branches([
      [
        Test(v('cur_mem'), c0),
        Set(b, val),
        mem(c0, ind, SetByAddrValue(addr, Fixed(val)))
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

C0 = program(
  0,
  lambda v: [Return(c0)]
)

C1 = program(
  0,
  lambda v: [Return(c1)]
)

MInterface = IterItem([
  func(StateMesIn(c0, Out(Up(AddrMes(a, x)))), StateMesOut(c1, Out(Down(AddrMes(a, x))))),
  func(StateMesIn(c1, Out(Down(a))), StateMesOut(c0, Out(Up(a))))
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
    Call(v('mesA'), A, Up(v('mes'))),
    Branches([
      [
        Parse(Down(v('mesAB')), mesA),
        Call(v('mesBA'), X, v('mesAB')),
        accBitDelta(v('b'), v('d'), v('mesBA')),
        Branches([
          [Test(v('d'), c1), Set(v('b'), c0)],
          [Test(v('d'), c0)]
        ]),
        Set(v('d1'), Func("DebugD")(v('d'))),
        Set(v('d2'), Func("DebugShift")(v('b'))),
        Call(mesA, A, Down(v('b'))),
        Back()
      ],
      [
        Parse(Up(v('mes')), v('mesA')),
        Return(v('mes'))
      ]
    ])
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

HybridM1 = program(
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
          ]
        ]),
      ]
    ]),
    Return(v('ret'))
  ]
)

HybridM2 = program(
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
 
MInterface = MInterface.tighten()

MX = MInterface(X)
MY = MInterface(Y)

HybridM = HybridM.tighten()
HybridM1 = HybridM1.tighten()
HybridM2 = HybridM2.tighten()
MImitate = MImitate.tighten()
ButOne = ButOne.tighten()
Shift = Shift.tighten()

breadth_first_search_diff_mem(
  HybridM(MX, MY)(C0), MX, 
  partition=Partition([(["0"], x), (["1"], x)]),
  cbk=Dumper("dumps/hybrid-0.txt")
)

breadth_first_search_diff_mem(
  HybridM(MX, MY)(C1), MY, 
  partition=Partition([(["0"], x), (["1"], x)]),
  cbk=Dumper("dumps/hybrid-1.txt")
)

breadth_first_search_diff_mem(
  Shift(HybridM(MX, MY)), HybridM1(MImitate(MX), MY), 
  partition=Partition([(["0"], x), (["1"], x)]),
  cbk=Dumper("dumps/hybrid-x-imitate.txt")
)

breadth_first_search_diff_mem(
  HybridM(MX, MY), HybridM2(MX, MImitate(MY)), 
  partition=Partition([(["0"], x), (["1"], x)]),
  cbk=Dumper("dumps/hybrid-y-imitate.txt")
)

breadth_first_search_diff_mem(
  HybridM1(ButOne(MX, Z), MY), HybridM2(MX, ButOne(MY, Z)),
  partition=Partition([(["0"], x), (["1"], x)]),
  cbk=Dumper("dumps/hybrid-x-y-swap.txt")
)
