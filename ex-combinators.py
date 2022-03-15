from core.iterProg import *
from core.term import func, norm, Term, Func, Const, Var, termToStr
from core.notation import *
from core.iterAlgebra import comp, IterItem, iter_var, carthesian
from core.iterDiff import breadth_first_search_diff, mode0
from core.log import Dumper, printl
from core.iterProgStandard import composition, composition2, callCbk, callCbk2

X = iter_var('X')
Y = iter_var('Y')
Z = iter_var('Z')

I = program(
  1,
  lambda v, F: [
    Message(v('mes')),
    Call(v('mes'), F, v('mes')),
    Return(v('mes'))
  ]
).tighten()

K = program(
  2,
  lambda v, F, G: [
    Message(v('mes')),
    Call(v('mes'), F, v('mes')),
    Return(v('mes'))
  ]
).tighten()

B = program(
  3,
  lambda v, F, G, H: [
    Message(v('mes')),
    callCbk(
      v('mes'), F, v('mes'), 
      lambda m: callCbk(m, G, m, lambda m2: Call(m2, H, m2))
    ),
    Return(v('mes'))
  ]
).tighten()

C = program(
  3,
  lambda v, F, G, H: [
    Message(v('mes')),
    callCbk2(
      v('mes'), F, v('mes'), 
      lambda m: Call(m, H, m),
      lambda m: Call(m, G, m)
    ),
    Return(v('mes'))
  ]
).tighten()

S = program(
  3,
  lambda v, F, G, H: [
    Message(v('mes')),
    callCbk2(
      v('mes'), F, v('mes'), 
      lambda m: Call(m, H, m),
      lambda m: callCbk(m, G, m, lambda m2: Call(m2, H, m2))
    ),
    Return(v('mes'))
  ]
).tighten()

print("Composition")
breadth_first_search_diff(
  composition(X, Y).tighten(), 
  X(Y).tighten(), 
  cbk=Dumper("dumps/composition.txt")
)

#exit(0)

print("Composition2")
breadth_first_search_diff(
  composition.tighten(), 
  composition2.tighten(), 
  cbk=Dumper("dumps/composition2.txt")
)

print("B")
breadth_first_search_diff(
  B(X, Y, Z), 
  X(Y(Z)), 
  cbk=Dumper("dumps/combinators-B.txt")
)

print("C")
breadth_first_search_diff(
  C(X, Y, Z), 
  X(Z, Y), 
  cbk=Dumper("dumps/combinators-C.txt")
)

print("K")
breadth_first_search_diff(
  K(X, Y), 
  X, 
  Dumper("dumps/combinators-K.txt")
)

print("SKK=I")
breadth_first_search_diff(
  S(K, K), 
  I, 
  cbk=Dumper("dumps/combinators-SKK.txt")
)

print("B=S(KS)S")
breadth_first_search_diff(
  B, 
  S(K(S), K), 
  cbk=Dumper("dumps/combinators-B-SKSS.txt")
)

print("C = (S (S (K (S (K S) K)) S) (K K))")
formula = S(S(K(S(K(S), K)), S), K(K))
breadth_first_search_diff(
  C, 
  formula, 
  cbk=Dumper("dumps/combinators-C-SSKSKSKSKK.txt")
)

print("S")
breadth_first_search_diff(
  S(X, Y, Z), 
  X(Z, Y(Z)), 
  no_debug=True
)
