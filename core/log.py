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
