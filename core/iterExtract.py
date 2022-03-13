from .iterAlgebra import IterItem
from .notation import *
from .term import func

s = Var('s')
x = Var('x')
z = Var('z')


def lib_call_to_comp_op(it, name):
  it = func(
    func(z, StateMes(s, OutMes(x))),
    func(z, StateMes(s, OutMes(UpMes(x))))
  ).applyGently(it)
  it = func(
    func(StateMes(s, OutMes(x)), z),
    func(StateMes(s, OutMes(UpMes(x))), z)
  ).applyGently(it)
  it = func(
    func(z, StateMes(s, CallMes(name, x))),
    func(z, StateMes(s, OutMes(DownMes(x))))
  ).applyGently(it)
  it = func(
    func(StateMes(s, CallMes(name, x)), z),
    func(StateMes(s, OutMes(DownMes(x))), z)
  ).applyGently(it)
  return it

def lib_call_to_comp(f, name):
  return IterItem([lib_call_to_comp_op(it, name) for it in f])
