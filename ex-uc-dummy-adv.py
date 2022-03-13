from core.iterDebug import runOnSeq
from core.log import printl
from core.term import func, norm, Term, Func, Const, Var, termToStr
from core.notation import *
from core.iterAlgebra import comp, IterItem, iter_var
from core.iterEq import automaton_diff, print_diff, backtrace_func_diff
from core.iterExpr import automaton_expression
from core.iterProg import *
from core.iterMem import breadth_first_search_diff_mem, test_print
from core.iter import tighten, tighten_iter
from uc.ucnet import Exec, DummyAdv, SystemMes, UserMes, AdvMes


def callCbk(ret, F, mes, cbk):
  return lambda v: [
#    Set(v('bugCbk'), Func('DebugIn3',3)(ret, mes, Const(str(F)))),
    Call(ret, F, UpMes(mes)),
#    Set(v('bugCbk'), Func('DebugOut3',3)(ret, mes, Const(str(F)))),
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
#          Set(v('bug1'), Func('Debug1',2)(m, v('zMes'))),
#          Call(m, A, AdvMes(v('zMes')))
          callCbk(m, A, m, lambda mA: [
#            Set(v('bug2'), Func('Debug2',1)(mA)),
            Call(mA, Exec, AdvMes(mA))
          ])
        ]      
      ])
    ]),
    Return(v('mes'))
  ], print_desc=True
)


Z = iter_var('Z')
A = iter_var('A')
N = iter_var('N')

#Dbg = tighten(
#  AdvZ.tighten()(Z, A)(
#Dbg = AdvZ(Z, A, no_tighten=True)(
#    Exec(DummyAdv, N, no_tighten=True), 
#    no_tighten=True
#  )#, include_all=True)
#printl()

#runOnSeq(Dbg, [
#  OutMes(x),
#  CallMes(Const("var_Z"), StateMes(x, OutMes(DownMes(AdvMes(y))))),
#  CallMes(Const("var_A"), StateMes(x, OutMes(DownMes(y))))
#])

AdvZ = AdvZ.tighten()
Exec = Exec.tighten()
DummyAdv = DummyAdv.tighten()

#breadth_first_search_diff_mem(Comp(X, Y), X(Y))
#breadth_first_search_diff_mem(Z(Exec(A, N)), AdvZ(Z, A)(Exec(A, N)), test_print)
#breadth_first_search_diff_mem(AdvZ, automaton_expression(1,2))
def check_message_sent(n, h, hf):
  printl(hf)
  print(n.term().args[2].args[1])
  pass

breadth_first_search_diff_mem(Z(Exec(A, N)), AdvZ(Z, A, Exec(DummyAdv, N)), cbk=check_message_sent)
#printl(AdvZ(Z, A, Exec(DummyAdv, N)))

