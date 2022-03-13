from core.term import func, norm, Term, Func, Const, Var, termToStr
from core.notation import *
from core.iterAlgebra import comp, IterItem, iter_var
from core.iterEq import automaton_diff, print_diff, backtrace_func_diff
from core.iterExpr import automaton_expression
from core.iterMem import breadth_first_search_diff_mem
from core.log import printl

X = iter_var('X')
Y = iter_var('Y')
Z = iter_var('Z')
I = automaton_expression(1)
Comp = automaton_expression((1, 2))
B = automaton_expression((1, (2, 3)))
K = automaton_expression((1), 2)
S = automaton_expression((1, 3, (2, 3)))
C = automaton_expression(((1, 3), 2))

print("B")
breadth_first_search_diff_mem(B(X, Y, Z), X(Y(Z)))
#print_diff(automaton_diff(B(X, Y, Z), X(Y(Z))))
print("K")
#printl(K)
print_diff(automaton_diff(K(X, Y), X))

print("SKK=I")

print_diff(automaton_diff(S(K, K), I))

print("B=S(KS)S")
print_diff(automaton_diff(B, S(K(S), K)))

print("C = (S (S (K (S (K S) K)) S) (K K))")
print_diff(automaton_diff(C, S(S(K(S(K(S), K)), S), K(K))))

print("S")
print_diff(automaton_diff(S(X, Y, Z), X(Z, Y(Z))))

#print_diff(automaton_diff(X(I), X(I(I))))
#backtrace_func_diff(S(X, Y, Z), X(Z, Y(Z)))