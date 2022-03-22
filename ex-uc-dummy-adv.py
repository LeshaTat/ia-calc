from core.iterDebug import runOnSeq
from core.iterProgStandard import callCbk
from core.log import Dumper, printl
from core.term import func, norm, Term, Func, Const, Var, termToStr
from core.notation import *
from core.iterAlgebra import comp, IterItem, iter_var
from core.iterProg import *
from core.iterDiffMem import breadth_first_search_diff_mem, test_print
from core.iter import tighten, tighten_iter
from uc.ucnet import Exec, DummyAdv, SystemMes, UserMes, AdvMes

AdvZ = program(
  3,
  lambda v, Z, A, Exec: [
    Message(v('mes')),
    callCbk(v('mes'), Z, v('mes'), lambda m: [
      Branches([
        [
          Parse(UserMes(v('zMes')), m),
          Call(m, Exec, UserMes(v('zMes')))
        ],
        [
          Parse(SystemMes(v('zMes')), m),
          Call(v('tmp'), Exec, SystemMes(v('zMes'))),
          callCbk(m, A, SystemMes(v('zMes')), lambda mA: Call(mA, Exec, AdvMes(mA))),
          Test(m, c0),
          Set(v('mes'), c0)
        ],
        [
          Parse(AdvMes(v('zMes')), m),
          callCbk(m, A, m, lambda mA: [
            Call(mA, Exec, AdvMes(mA))
          ])
        ]      
      ])
    ]),
    Return(v('mes'))
  ]
)

Z = iter_var('Z')
A = iter_var('A')
N = iter_var('N')

AdvZ = AdvZ.tighten()
Exec = Exec.tighten()
DummyAdv = DummyAdv.tighten()

breadth_first_search_diff_mem(
  Z(Exec(A, N)), 
  AdvZ(Z, A)(Exec(DummyAdv, N)), 
  cbk=Dumper("dumps/uc-dummy-adv")
)