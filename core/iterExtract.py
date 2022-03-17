from .iterAlgebra import IterItem
from .notation import *
from .term import func

s = Var('s')
x = Var('x')
z = Var('z')

def lib_call_to_comp_op(it, name):
  it = func(
    func(z, StateMesOut(s, Out(x))),
    func(z, StateMesOut(s, Out(Up(x))))
  ).applyGently(it)
  it = func(
    func(StateMesIn(s, Out(x)), z),
    func(StateMesIn(s, Out(Up(x))), z)
  ).applyGently(it)
  it = func(
    func(z, StateMesOut(s, Lib(name, x))),
    func(z, StateMesOut(s, Out(Down(x))))
  ).applyGently(it)
  it = func(
    func(StateMesIn(s, LibRet(name, x)), z),
    func(StateMesIn(s, Out(Down(x))), z)
  ).applyGently(it)
  return it

def lib_call_to_comp(f, name):
  return IterItem([lib_call_to_comp_op(it, name) for it in f])
