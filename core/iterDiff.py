from .term import ID, func, cortege, Var, Const, Func, pair, cortege, termToStr
from .notation import *
from .termAlgebra import listO, listApply, U, listIntersect, listPair, listApproxMinus, termTermApply

mode0 = ID(c0)
mode1 = ID(c1)
mode2 = ID(c2)
mode3 = ID(c3)

s = Var('s')
q = Var('q')
sf = Var('sf')
sg = Var('sg')
d = Var('d')
df = Var('df')
dg = Var('dg')
z = Var('z')
sn = Var('sn')
dn = Var('dn')
x = Var('x')
y = Var('y')
xg = Var('xg')
yg = Var('yg')
xf = Var('xf')
yf = Var('yf')
a = Var('a')
b = Var('b')
addr = Var('addr')
const_f = ID(Const('f'))
const_g = ID(Const('g'))

mem = Func("mem", 2)

refreshX = func(
  cortege(d, q, StateMes(sf, xf), StateMes(sg, yg), b),
  cortege(d, q, StateMes(sf, y), StateMes(sg, y), b)
)

changeC0  = func(
  cortege(d, q, StateMes(s, x), y, b),
  cortege(mode0, StateMes(s, x), StateMes(s, x), y, x)
)
changeC1  = func(
  cortege(d, q, x, StateMes(s, y), b),
  cortege(mode1, q, x, StateMes(s, y), y)
)
changeC2  = func(
  cortege(d, q, x, StateMes(s, y), b),
  cortege(mode2, StateMes(s, y), x, StateMes(s, y), y)
)
changeC3  = func(
  cortege(d, q, StateMes(s, x), y, b),
  cortege(mode3, q, StateMes(s, x), y, x)
)


def printl(l):
  print('[')
  for t in l:
    print(str(t.t))
  print(']')

def printlt(l):
  print('[')
  for t in l:
    print(termToStr(t)+",")
  print(']')
def printlt_q(l):
  print('[')
  for t in l:
    print(t)
  print(']')

class DegException(Exception):
  def __init__(self, start, call_history, not_done_arg):
    self.start = start
    self.call_history = call_history
    self.not_done_arg = not_done_arg

class DegCounter:
  def __init__(self, start):
    self.start = start
    self.count = 1
    self.is_done = False
    self.not_done_arg = None
  def done(self, arg, arg_term):    
    self.is_done = self.is_done or self.start[0].term().args[1] == arg
    if not self.is_done:
      self.not_done_arg = arg_term
    else:
      self.not_done_arg = None
  def inc(self, num):
    self.count = self.count + num
  def dec(self, call_history):
    self.count = self.count - 1
    if self.count<=0 and not self.is_done:
      raise DegException(self.start, call_history, self.not_done_arg)

class UsedGrouped:
  def __init__(self):
    self.used = {}
  def add(self, state, no_change=False):
    if state.isEmpty():
      return False
    l = self.used.get(state.getGroupID(), [])
    if state.isIn(l):
      return False
    if not no_change:
      l.append(state)
      self.used[state.getGroupID()] = l
    return True

class DiffState:
  def __init__(self, t, identifier = 0):
    self.t = t
    self.fApplied = None
    self.identifier = identifier

  def clone(self):
    return DiffState(self.t, self.identifier)

  def term(self):
    return self.t

  def replace_term(self, addr, v):
    self.t = self.t.replace(addr, v)

  def applyList(self, l):
    nxt = []
    for fOne in l: self.applyTerm(fOne).appendToList(nxt)
    return nxt
  
  def applyTerm(self, f, save_f_applied=False):
    nxt = self.clone()
    nxt.t = termTermApply(f, self.t)
    if save_f_applied:
      nxt.fApplied = f
    return nxt

  def appendToList(self, l):
    if self.t.isEmpty() or self.isInList(l):
      return l
    l.append(self)
    return l

  def isInOne(self, other):
    if not self.t.s==other.t.s:
      return False
    return True
  
  def isInList(self, l):
    for m in l:
      if self.isInOne(m): return True
    return False    

class StateModel:
  def __init__(self, model, h, hf, hg, deg = None, identifier = 0):
    self.model = model
    self.h = h
    self.hf = hf
    self.hg = hg
    self.deg = deg
    self.identifier = identifier
    self.fApplied = None
  def isEmpty(self):
    return self.model.t.isEmpty()
  def getGroupID(self):
    return self.model.t.groupID
  def isIn(self, l):
    for state2 in l:
      if self.model.isInOne(state2.model):
        return True
    return False


def breadth_first_search_diff(f, g, cbk=None):
  nxt = [
    StateModel(DiffState(
      cortege(mode0, StateMes(c0, x), StateMes(c0, x), StateMes(c0, x), x), identifier=(0, 1)
      ), [], [], [], deg = None),
    StateModel(DiffState(
      cortege(mode2, StateMes(c0, x), StateMes(c0, x), StateMes(c0, x), x), identifier=(0, 1)
      ), [], [], [], deg = None)
  ]
  ff = func(func(x, y), func(cortege(d, q, x, a, b), cortege(d, q, y, a, b)))(f)
  gg = func(func(x, y), func(cortege(d, q, a, x, b), cortege(d, q, a, y, b)))(g)

  cnt = 2

  used = UsedGrouped()
  used.add(nxt[0])
  used.add(nxt[1])
  max_default = 0
  max_hlen = 0
#  wait_f = {}
#  wait_g = {}
  try:
    while nxt:
      cur = nxt
      nxt = []
      def add_nxt(state, add=False):
        if not used.add(state, no_change=not add): return
#        if n.term().args[0]==c1:# and not deg:
#          print("HERE IS IT")
        nxt.append(state)
      for state in cur:
        c = state.model
        identifier = c.identifier
        h = state.h
        hf = state.hf
        hg = state.hg
        deg = state.deg
        ct = c.term()
        mode = ct.args[0]
        cf = ct.args[2]
        cg = ct.args[3]
        cNext = []
        if mode in (mode0, mode3):
          cNext = c.applyList(ff)
        elif mode in (mode1, mode2):
          cNext = c.applyList(gg)
#        if len(c.default.l)>max_default:
#          max_default = len(c.default.l)
#          print(max_default)
        if len(hf)>max_hlen and False:
          max_hlen = len(hf)
          print("HLen: "+str(max_hlen))
          print(len(cur))
          if max_hlen==10:
            for i, cc in enumerate(cur):
              print("----------- "+str(i))
              test_print(cc[0])
              print("\n---\n")
              print(cc[0].t.groupID)
              print(cc[0].term().groupID)
              print("\n\n".join([str(arg) for arg in cc[0].term().args]))
              print("---")
              printlt_q(cc[3])
            print(len(cur))
            exit(0)
      
        if deg is not None:
          deg.inc(len(cNext))
          deg.dec(hf if mode in (mode0, mode3) else hg)
        for n in cNext:
          nt = n.term() 
          nArgX = nt.args[1]
          nf = nt.args[2]
          ng = nt.args[3]

          hNext = h

          ndeg = deg
          if mode == mode0:
            nhf = hf
            if nf.isIn(StateMes(s, x)):
  #           wait_f[str(pair(nArgX, nf).norm)] = h + [n]
              hNext = h + [n]   
              nhf = hf + [n.term().args[4]]
              n = n.applyTerm(changeC1, save_f_applied=True)
              ndeg = DegCounter((n, hNext, nhf, ng))
            else:
              hNext = h + [n]   
            add_nxt(StateModel(n, hNext, nhf, hg, ndeg), add=True)
          elif mode == mode1:
            if ng.isIn(StateMes(s, x)):
              deg.done(nArgX, nt)
  #            del wait_f[str(pair(nArgX, nf).norm)]
              if not nt.isIn(cortege(a, q, StateMes(s, y), StateMes(d, y), b)):
                print("Diff found for " + str(n.t))
#                print("\nLast applied term\n")
#                print(str(n.fApplied))
                print("\n")
                printlt_q(hf)
                printlt_q(hg)
                print_history(h+[n])
                return
              nhg = hg + [n.term().args[4]]
              deg.dec(nhg)
#              deg = None
              if cbk is not None:# and not n.isIn(used):
                cbk(n, h)
              hNext = h + [n]
              n = n.applyTerm(refreshX, save_f_applied=True)
              n = n.applyTerm(changeC0, save_f_applied=True)
              cnt = cnt + 1
              identifier = (identifier[1], cnt)
              n.identifier = identifier
              n2 = n.applyTerm(changeC2)
              hNext2 = h + [n2]   
              add_nxt(StateModel(n, hNext, hf, nhg), add=True)
              add_nxt(StateModel(n2, hNext2, hf, nhg), add=True)
            else:
              hNext = h# + [n]   
              add_nxt(StateModel(n, hNext, hf, hg, deg), add=True)
          elif mode == mode2:
            nhg = hg
            if ng.isIn(StateMes(s, x)):
    #          wait_g[str(pair(nArgX, ng).norm)] = h + [n]
              hNext = h + [n]   
              nhg = hg + [n.term().args[4]]                
              n = n.applyTerm(changeC3)
              ndeg = DegCounter((n, hNext, hf, nhg))
            else:
              hNext = h + [n]   
            add_nxt(StateModel(n, hNext, hf, nhg, ndeg), add=True)
          elif mode == mode3:
            nhf = hf
            if nf.isIn(StateMes(s, x)):
              nhf = hf + [n.term().args[4]]
              deg.done(nArgX, nt)
              deg.dec(nhf)
    #          del wait_g[str(pair(nArgX, ng).norm)]
              continue
            else:
              hNext = h# + [n]   
            add_nxt(StateModel(n, hNext, nhf, hg, deg), add=True)
  #  if wait_f or wait_g:
  #    print("Degradation found")
  #    print("For f: ")
  #    for k, hl_f in wait_f.items():
  #      print(k)
  #      for h_f in hl_f:
  #        print(h_f.t)
  #    print("For g: ")
  #    for k, hl_g in wait_g.items():
  #      print(k)
  #      for h_g in hl_g:
  #        print(h_g.t)
  #    return
    print("Diff not found")
  except DegException as e:
    print("Diff degradation found for")
    print("\n\n".join([str(arg) for arg in e.start[0].term().args]))
    if e.not_done_arg:
      print('EXPECTED ARG: '+str(e.start[0].term().args[1]))
      print('NOT DONE ARG: '+str(e.not_done_arg))
    print('---')    
    print_history(e.start[1])
#    printlt([func(
#      cortege(z, q, StateMes(s, x), StateMes(d, y), b),
#      cortege(x, y, z, b)
#    )(t.term()) for t in e.start[1]])
    print('--- CALL HISTORY ---')
    printlt(e.call_history)
    raise e

def test_print(n):
  t = n.term()
  inp = t.args[1].args[1]
  mes = t.args[2].args[1]
  mes2 = t.args[3].args[1]
  st1 = t.args[2].args[0]
  st2 = t.args[3].args[0]
  (fId, tId) = n.identifier
#  print("Applied: \n"+str(n.fApplied)+"\n")
  print("States: \n"+str(st1)+'\n'+str(st2)+"\n")
  print(str(fId)+', '+str(inp)+" -> \n"+str(tId)+', '+str(mes))
  if str(mes2)!=str(mes):
    print(str(mes2))
  print("")

def print_history(h):
  for it in h:
    test_print(it)