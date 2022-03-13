from .notation import *
from .term import func
from .termAlgebra import listApply

x = Var('x')
d = Var('d')

def printfl(l):
  print('[')
  for t in l:
    print(str(t.args[0])+' ->\n'+str(t.args[1])+'\n')
  print(']')

def printl(l):
  print('[')
  for t in l:
    print(t)
  print(']')

s = Var('s')

def runOnSeq(f, seq, partition=None):
  nxt = [(StateMes(c0, seq[0]), [], 0)]
  while nxt:
    cur = nxt
    nxt = []
    for (cX, h, i) in cur:
      cNext = cX.applyBy(f)
      if not cNext and i == len(seq)-1:
        print('\nEND VARIANT')
        printl(h + [Const('STOPPED')])

      for n in cNext:
        ci = i
        if n.isIn(StateMes(s, x)):
          print(n.args[0])
          print(n.args[1])
          print('')
          if i+1 >= len(seq): 
            nxt.append((n, h+[n], i+1))
            break
          seqI = seq[i+1]
          ci = i+1
          sX = seqI.genNewVar('s')
          xX = seqI.genNewVar('x')
          h = [Func("OUTPUT", 1)(n.args[1])]
          n = func(StateMes(sX, xX), StateMes(sX, seqI))(n)          
        nxt.append((n, h+[n], ci))
      if i >= len(seq): break
    if i >= len(seq): break
  if nxt:
    for nxt_l in nxt:
      printl(nxt_l[1])    
