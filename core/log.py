from .notation import mode0

def printl(l):
  print('[')
  for t in l:
    print(str(t))
  print(']')

def printlf(l):
  print('[')
  for t in l:
    print(str(t.args[0])+' ->\n'+str(t.args[1])+'\n')
#    print(str(t.argsc0.groupID)+' ->\n'+str(t.argsc1.groupID)+'\n')
  print(']')

class Dumper:
  def __init__(self, filename=None):
    self.i = 0
    if filename is not None:
      self.file = open(filename+".txt", "w")
      self.file2 = open(filename+"-fstate.txt", "w")
    else:
      self.file = None
      self.file2 = None
  def close(self):
    if self.file:
      self.file.close()
    if self.file2:
      self.file2.close()
  def print(self, s=None):
    if self.file:
      self.file.write(str(s)+"\n")
    else:
      print(s)
  def print2(self, s=None):
    if self.file2:
      self.file2.write(str(s)+"\n")
  def __call__(self, n, h, hf=None, is_last=False):
    if not is_last: 
      return
    self.i = self.i + 1
    self.print("*** "+str(self.i)+" ***")
    self.print2("*** "+str(self.i)+" ***")
    for c in h:
      if c.term().args[0]!=mode0:
        continue
      self.print(str(c.term().args[1].args[1])+" ->")
      self.print(str(c.term().args[2].args[1]))
      self.print("")
      self.print2("STATE: " + str(c.term().args[1].args[0]))
      self.print2("MES:" + str(c.term().args[1].args[1])+" ->")
      self.print2("STATE: " + str(c.term().args[2].args[0]))
      self.print2("MES: " + str(c.term().args[2].args[1]))
      self.print2("")
    pass
