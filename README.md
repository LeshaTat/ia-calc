# Basic Iterative Automaton Calculator

This project is intended to provide a minimalistic abstract interpretation-based framework capable to mechanizing black-box reduction-based proofs in computational settings.

The work is in the early stage of development.

## Current status: proof-of-concept, DRAFT

* Theoretical paper: [draft version](ia-calc.pdf). The framework itself and example mechanized proofs are presented in full. For most technical statements, the proof is currently abscent.
The theory of polynomial operator needs in-depth check.
* Algorithm implementations. They do work, but the code is not prepared for easy reading and is not annotated.

## Examples of mechanized proofs

Each example consists of three parts: 
programs for used iterative automatons, 
a list of proved equalities,
dump files for proofs of those equivalences.

Program syntax in python files slightly differs from one described
in the paper, but semantics is the same.

Dump files consist of an enumeration of some variants of input sequences that the algorithm has brute-forced through.

The algorithm is not originally designed to provide such dumps. We added 
heuristic to generate those logs, but results may not be accurate. 
In particular, 1. the variable names differ between calls, 2. some sequences are duplicated, 3. some variants may be absent (but they shouldn't).


## Example 1. Combinators 

In [ex-combinators.py](ex-combinators.py) we provide definitions for combinators I, K, B, C, S and checks the following equations:
[K x y = x](dumps/combinators-K.txt), [B x y z= x (y z)](dumps/combinators-B.txt), [C x y z = x z y](dumps/combinators-C.txt), [S K K = I](dumps/combinators-SKK.txt), [B = S (K S) S](dumps/combinators-B-SKSS.txt), [C = (S (S (K (S (K S) K)) S) (K K))](dumps/combinators-C-SSKSKSKSKK.txt). Also we checks that
[composition x y = x y](dumps/composition.txt) and [composition2 = composition](dumps/composition2.txt), see the paper for the details.

Note that execution of this example fails on the equation
S x y z = (x z) (y z). This is the intended behavior, the equation is wrong because z's on the right side would have separated states.

## Example 2.1. UC: Dummy Adversary Theorem

In [uc/ucnet.py](uc/ucnet.py) we provide definitions for Exec, Net and DummyAdv automatons. 

The example [ex-uc-dummy-adv.py](ex-uc-dummy-adv.py) contains a definition for AdvZ automaton and of the following automaton equation

[Z(Exec(A, N)) = AdvZ(Z, A)(Exec(DummyAdv, N))](dumps/uc-dummy-adv.txt),

where Z, A and N are arbitrary iterative automatons.

## Example 2.2. UC: Composition Theorem

In this example, we use iterative automaton UComp from [uc/ucnet.py](uc/ucnet.py), while the rest of automatons are defined alongside equivalence checks
in [ex-uc-composability.py](ex-uc-composability.py).

The theorem states that if 

Exec(DummyAdv,Net(Q,H)) =_P Exec(SQ,Net(DummyP,G))

and

Exec(DummyAdv,Net(P,G)) =_P Exec(SP,Net(DummyP,F))

then

Exec(DummyAdv,Net(UComp(P,Q),H)) =_P Exec(SPQ(SP, SQ),Net(DummyP,F))

for arbitrary P, Q, H, F, G (with some conditions on their polynomiality).
Note that SPQ is a fixed iterative automaton, not a variable.

To prove this we provide a sequence of equivalences, some of them 
are implications of the properties of =_P relation, while others
are checked by the algorithm.

[Exec(DummyAdv, Net(UComp(P, Q), H)) = T1(P)(Exec(DummyAdv, Net(Q, H)))](dumps/uc-comp-P-Q.txt)

T1(P)(Exec(DummyAdv, Net(Q, H))) =_P T1(P)(Exec(SQ, Net(DummyP, G)))

[T1(P)(Exec(SQ, Net(DummyP, G))) = T2(SQ)(Exec(DummyAdv, Net(P, G)))](dumps/uc-comp-P-SQ.txt)

T2(SQ)(Exec(DummyAdv, Net(P, G))) =_P T2(SQ)(Exec(SP, Net(DummyP, F)))

[T2(SQ)(Exec(SP, Net(DummyP, F))) = Exec(SPQ(SP, SQ), Net(DummyP, F))](dumps/uc-comp-SPQ.txt)

Automatons T1 and T2 are also defined in [ex-uc-composability.py](ex-uc-composability.py).

## Example 2.3. UC: Authentication channel

Here we use a bunch of definitions

- [F_CA](ucauth/F_CA.py) - Certification Authority functionality
- [F_auth](ucauth/F_auth.py) - Authentication channel functionality
- [UCShell](uc/ucnet.py) - a wrapper necessary that separates protocol participants from each other
- [P_auth](ucauth/pauth.py) - authentication protocol based on signature; supposed to be wrapped inside UCShell(P_auth)
- [GameSignReal and GameSignIdeal](ucauth/euf_cma_sign.py) - games that defines a variant of EUF-CMA security for signature scheme

The list of technical automatons include

- [SimX_auth](ucauth/sim_auth.py) - simulator, that uses GameSign(Real/Ideal)
- [FX_auth](ucauth/F_auth.py) - modified Authentication channel functionality with some checks relinked to a GameSign(Real/Ideal)
- [PX_auth](ucauth/pauth.py) - modified authentication protocol based on GameSign(Real/Ideal)
- [lib2call](core/iterExtract.py) - a function that connects
an automaton to a library realization for specific library name (e.g. GameSign in our case).
- SimIdeal_auth = lib2call(GameSign, Sim_auth, SignGameIdeal)
- PReal_auth = lib2call(GameSign, PX_auth, SignGameIdeal)
- PIdeal_auth = lib2call(GameSign, PX_auth, SignGameIdeal)


We assume that GameSignReal =_P GameSignIdeal. Let's prove that

Exec(DummyAdv,Net(UCShell(P_auth),F_CA)) =_P
Exec(SimIdeal_auth, Net(UCShell(DummyP),F_auth))

First, replace all protocol calls to signature scheme with calls to GameSign
(see [ex-uc-auth-1.py](ex-uc-auth-1.py)).

[Exec(DummyAdv,Net(UCShell(P_auth),F_CA)) =A Exec(DummyAdv,Net(UCShell(PReal_auth),F_CA))](dumps/uc-auth-addsignlib.txt)

We can replace PReal_auth with PIdeal_auth because of the properties of =_P relation.

Exec(DummyAdv,Net(UCShell(PReal_auth),F_CA)) =_P Exec(DummyAdv,Net(UCShell(PIdeal_auth),F_CA))

In [ex-uc-auth-2.py](ex-uc-auth-2.py) we prove that this scheme is equivalent to the one with modified FX_auth functionality that shares requests to GameSign with PX_auth

[Exec(DummyAdv,Net(UCShell(PIdeal_auth),F_CA)) = lib2call(GameSign, Exec(SimX_auth, Net(UCShell(DummyP),FX_auth)), SignGameIdeal)](dumps/uc-auth-sim-simx.txt)

Finally, we show that

[lib2call(GameSign, Exec(SimX_auth, Net(UCShell(DummyP),FX_auth)), SignGameIdeal)= Exec(SimIdeal_auth, Net(UCShell(DummyP),F_auth))](dumps/uc-auth-simx.txt)

## Example 3. Hybrid Argument

All automatons are defined in [ex-hybrid.py](ex-hybrid.py).

We formulate a hybrid principle that incorporates a hybrid argument technique and mathematical induction.

Let H be a hybrid automaton that should be composed with another one to form either 

HA = H Const(0)

or

HB = H Const(1)

or something intermediate 

HX = H G.

The Shift automaton is made in such a way that Shift H = H', where H' in (H' G) gets one additional 0 compared to H in (H G).

We state that if H =_P H' then HA =_P HB and demonstrate an application of this theorem.

We call MX a multiplexor for X if MImitate(MX) =_P ButOne(MX, X). 
The automaton ButOne(MX, X)(G) works as MX if G always returns 0, or
it replaces one first call (roughly speaking) of MX to call to X, when G outputs first 1. The automaton MImitate(MX)(G) just ignores G, i.e. MImitate(MX)(G)=MX.

Suppose MA is a multiplexor for A and MB is an multiplexor for B, and A =_P B. We prove that MA =_P MB in this case.

First, we construct the automaton HybridM such that 
[HybridM(MA, MB)(Const(0))=_A MA](dumps/hybrid-0.txt) and
[HybridM(MA, MB)(Const(1))=_A MB](dumps/hybrid-1.txt).

Next, we prove the step of our hybrid induction

[Shift(HybridM(MX, MY))=HybridM1(MImitate(MX), MY)](dumps/hybrid-x-imitate.txt)

HybridM1(MImitate(MX), MY) =_P HybridM1(ButOne(MX, Z), MY)

[HybridM1(ButOne(MX, Z), MY)=HybridM2(MX, ButOne(MY, Z))](dumps/hybrid-x-y-swap.txt)

HybridM2(MX, ButOne(MY, Z)) =_P HybridM2(MX, MImitate(MY))

[HybridM2(MX, MImitate(MY))=HybridM(MX, MY)](dumps/hybrid-y-imitate.txt)

