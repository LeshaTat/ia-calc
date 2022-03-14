from argparse import _AppendAction
from .term import ID, func, cortege, Var, Const, Func, pair, cortege, termToStr
from .notation import *
from .termAlgebra import listO, listApply, U, listIntersect, listPair, listApproxMinus
#from .iterMap import MapModel
from .iterMap2 import MapStore as MapModel

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

refreshX = MapModel.extendFunc(func(
  cortege(d, q, StateMes(sf, xf), StateMes(sg, yg), b),
  cortege(d, q, StateMes(sf, y), StateMes(sg, y), b)
))

changeC0  = MapModel.extendFunc(func(
  cortege(d, q, StateMes(s, x), y, b),
  cortege(mode0, StateMes(s, x), StateMes(s, x), y, x)
))
changeC1  = MapModel.extendFunc(func(
  cortege(d, q, x, StateMes(s, y), b),
  cortege(mode1, q, x, StateMes(s, y), y)
))
changeC2  = MapModel.extendFunc(func(
  cortege(d, q, x, StateMes(s, y), b),
  cortege(mode2, StateMes(s, y), x, StateMes(s, y), y)
))
changeC3  = MapModel.extendFunc(func(
  cortege(d, q, StateMes(s, x), y, b),
  cortege(mode3, q, StateMes(s, x), y, x)
))

Debug = Const('Debug')
changeDebug0  = MapModel.extendFunc(func(
  cortege(d, q, StateMes(s, CallMes(Debug, x)), y, b),
  cortege(d, q, StateMes(s, CallMes(Debug, c0)), y, b)
))
changeDebug1  = MapModel.extendFunc(func(
  cortege(d, q, x, StateMes(s, CallMes(Debug, y)), b),
  cortege(d, q, x, StateMes(s, CallMes(Debug, c0)), y)
))

response_mem_f = lambda v: MapModel.extendFunc(func(
  cortege(d, q, StateMes(s, CallMes(x, y)), a, b),
  cortege(d, q, StateMes(s, CallMes(x, v)), a, CallMes(x, v))
))

response_mem_g = lambda v: MapModel.extendFunc(func(
  cortege(d, q, a, StateMes(s, CallMes(x, y)), b),
  cortege(d, q, a, StateMes(s, CallMes(x, v)), CallMes(x, v))
))

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
    self.used = []#{}
  def add(self, state, no_change=False):
    if state.isEmpty():
      return False
    if state.isIn(self.used):
      return False
    if not no_change:
      self.used.append(state)
    return True
    if state.isEmpty():
      return False
    l = self.used.get(state.getGroupID(), [])
    if state.isIn(l):
      return False
    if not no_change:
      l.append(state)
      self.used[state.getGroupID()] = l
    return True

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


def breadth_first_search_diff_mem(f, g, cbk=None, partition=None):
  nxt = [
    StateModel(
      MapModel(
        cortege(
          mode0, 
          StateMes(c0, x), 
          StateMes(c0, x), 
          StateMes(c0, x), 
          x
        ), 
        identifier=(0, 1),
        partition=partition
      ), 
      [], [], [], deg = None
    ),
    StateModel(
      MapModel(
        cortege(
          mode2, 
          StateMes(c0, x), 
          StateMes(c0, x), 
          StateMes(c0, x), 
          x
        ), 
        identifier=(0, 1),
        partition=partition
      ), 
      [], [], [], deg = None
    )
  ]
  ff = {}
  gg = {}
  for f_it in f:
    f_gr = ff.get(f_it.args[0].groupID, [])
    f_gr.append(MapModel.extendFunc(
      func(func(x, y), func(cortege(d, q, x, a, b), cortege(d, q, y, a, b)))(f_it)
    ))
    ff[f_it.args[0].groupID] = f_gr
  for g_it in g:
    g_gr = gg.get(g_it.args[0].groupID, [])
    g_gr.append(MapModel.extendFunc(
      func(func(x, y), func(cortege(d, q, a, x, b), cortege(d, q, a, y, b)))(g_it)
    ))
    gg[g_it.args[0].groupID] = g_gr

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
        if not used.add(state, no_change=not add): 
          return False
        nxt.append(state)
        return True
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
        try:
          if mode in (mode0, mode3):
            cNext = c.applyList(ff.get(cf.groupID, []), forbid_deg=mode==mode3)
          elif mode in (mode1, mode2):
            cNext = c.applyList(gg.get(cg.groupID, []), forbid_deg=mode==mode1)
        except BaseException as e:
          print(e)
          raise DegException((c, h, hf, hg), state.hg if mode == mode1 else state.hf, None)
      
        if deg is not None:
          deg.inc(len(cNext))
          deg.dec(hf if mode in (mode0, mode3) else hg)

        for n in cNext:
          nt = n.term() 
          nArgX = nt.args[1]
          nf = nt.args[2]
          ng = nt.args[3]

          hNext = h
          try:
            if nf.isIn(StateMes(s, CallMes(Debug, x))):
              nhf = hf + [n.term().args[2].args[1]]   
              hNextMem = h + [n]
              n = n.applyTerm(changeDebug0, save_f_applied=True)
              add_nxt(StateModel(n, hNextMem, nhf, hg, deg), add=True)
              continue

            if ng.isIn(StateMes(s, CallMes(Debug, x))):
              nhg = hg + [n.term().args[3].args[1]]   
              hNextMem = h + [n]
              n = n.applyTerm(changeDebug1, save_f_applied=True)
              add_nxt(StateModel(n, hNextMem, hf, nhg, deg), add=True)
              continue
            
            if nf.isIn(StateMes(s, CallMes(Mem(x), y))):
              ind = pair(const_f, nf.args[1].args[0].args[0])
              arg = nf.args[1].args[1]
              addr = arg.args[0]
              mem_res = n.enum_all_possibilities(ind, addr)
              added = False
              for n_mem in mem_res:
                val = c0
                hNextMem = h + [n]
                if arg.name == "GetByAddr":
                  val = n_mem.get_by_ind(ind, addr)
                else:
                  val = arg.args[1]
                  n_mem.put_key_val_by_ind(ind, addr, val)
                  val = c0
                hNextMem = hNextMem + [n_mem]
                n_mem.replace_term([2,1,1], val)
                hNextMem = hNextMem + [n_mem]   
                nhf = hf + [pair(n_mem.term().args[2].args[1], arg)]   
                added_cur = add_nxt(StateModel(n_mem, hNextMem, nhf, hg, deg), add=True)
                added = added or added_cur
              if cbk is not None and not added:
                cbk(n, h, hf, is_last=not added)
              continue

            if ng.isIn(StateMes(s, CallMes(Mem(x), y))):
              ind = pair(const_g, ng.args[1].args[0].args[0])
              arg = ng.args[1].args[1]
              addr = arg.args[0]
              val = c0
              mem_res = n.enum_all_possibilities(ind, addr)
              added = False
              for n_mem in mem_res:
                val = c0
                hNextMem = h + [n]
                if arg.name == "GetByAddr":
                  val = n_mem.get_by_ind(ind, addr)            
                else:
                  val = arg.args[1]
                  n_mem.put_key_val_by_ind(ind, addr, val)
                  val = c0
                hNextMem = hNextMem + [n_mem]
                n_mem.replace_term([3,1,1], val)
                nhg = hg + [pair(n_mem.term().args[3].args[1], arg)]   
                hNextMem = hNextMem + [n_mem]   
                added = add_nxt(StateModel(n_mem, hNextMem, hf, nhg, deg), add=True)
                added = added or added_cur
              if cbk is not None and not added:
                cbk(n, h, hg, is_last=not added)
              continue
          except BaseException as e:
            print_history(h+[n])
            raise e
            return

          ndeg = deg
          if mode == mode0:
            nhf = hf
            n_prev = n
            if not nf.isIn(StateMes(s, x)):
              raise BaseException("Incorrect automaton output")
            hNext = h + [n]   
            nhf = hf + [n.term().args[4]]
            n = n.applyTerm(changeC1, save_f_applied=True)
            ndeg = DegCounter((n, hNext, nhf, ng))
            added = add_nxt(StateModel(n, hNext, nhf, hg, ndeg), add=True)
            if cbk is not None and not added:
              cbk(n_prev, hNext, nhf, is_last=not added)
          elif mode == mode1:
            if not ng.isIn(StateMes(s, x)):
              raise BaseException("Incorrect automaton output")
            deg.done(nArgX, nt)
#            del wait_f[str(pair(nArgX, nf).norm)]
            if not nt.isIn(cortege(a, q, StateMes(s, y), StateMes(d, y), b)):
              print("Diff found for " + str(n.t))
#                print("\nLast applied term\n")
#                print(str(n.fApplied))
              print("\n")
              printlt_q(hf)
              printlt_q(hg)
              printlt(hf)
              printlt(hg)
              print_history(h+[n])
              return
            nhg = hg + [n.term().args[4]]
            deg.dec(nhg)
#              deg = None
            if cbk is not None:# and not n.isIn(used):
              cbk(n, h, hf)
            hNext = h + [n]
            n_prev = n
            n = n.applyTerm(refreshX, save_f_applied=True)
            n = n.applyTerm(changeC0, save_f_applied=True)
            cnt = cnt + 1
            identifier = (identifier[1], cnt)
            n.identifier = identifier
            n2 = n.applyTerm(changeC2)
            hNext2 = h + [n2]   
            added = add_nxt(StateModel(n, hNext, hf, nhg), add=True)
            add_nxt(StateModel(n2, hNext2, hf, nhg), add=True)
            if cbk is not None:
              cbk(n_prev, hNext, nhg, is_last=not added)
          elif mode == mode2:
            nhg = hg
            if not ng.isIn(StateMes(s, x)):
              raise BaseException("Incorrect automaton output")
            hNext = h + [n]   
            nhg = hg + [n.term().args[4]]                
            n = n.applyTerm(changeC3)
            ndeg = DegCounter((n, hNext, hf, nhg))
            add_nxt(StateModel(n, hNext, hf, nhg, ndeg), add=True)
          elif mode == mode3:
            nhf = hf
            if not nf.isIn(StateMes(s, x)):
              raise BaseException("Incorrect automaton output")
            nhf = hf + [n.term().args[4]]
            deg.done(nArgX, nt)
            deg.dec(nhf)
            continue
            add_nxt(StateModel(n, hNext, nhf, hg, deg), add=True)
    print("Diff not found")
    if cbk and getattr(cbk, "close", None) is not None:
      cbk.close()
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
    printlt_q(e.call_history)
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
  print(str(n.layers.keys()))
  print(str(n.blocks.keys()))
#  if n.was_put:
#    print(str(n.was_put[0])+", "+str(n.was_put[1])+', '+str(n.was_put[2]))
  print(",".join([str(ind)+": "+str(k)+"="+str(v) for ind, k, v in n.d])+"\n")
  print(str(fId)+', '+str(inp)+" -> \n"+str(tId)+', '+str(mes))
  if str(mes2)!=str(mes):
    print(str(mes2))
  print("")

def print_history(h):
  for it in h:
    test_print(it)