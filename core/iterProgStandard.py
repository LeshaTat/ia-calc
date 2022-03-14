from core.iterProg import *

def lib(ret, F, mes):
  return lambda v: [
    Call(ret, F, mes),
  ]

def mem(ret, k, mes):
  return lambda v: [
    Call(ret, Mem(k), mes),
  ]

composition = program(
  2,
  lambda v, F, G: [
    Message(v('mes')),
    Call(v('mesA'), F, UpMes(v('mes'))),
    Branches([
      [
        Parse(DownMes(v('mesAB')), v('mesA')),
        Call(v('mesBA'), G, v('mesAB')),
        Call(v('mesA'), F, DownMes(v('mesBA'))),
        Back()
      ],
      [
        Parse(UpMes(v('mes')), v('mesA')),
        Return(v('mes'))
      ]
    ])
  ]
).tighten()

def callCbk(ret, F, mes, cbk):
  return lambda v: [
    Call(v('mesA'), F, UpMes(mes)),
    Branches([
      [
        Parse(DownMes(v('mesAB')), v('mesA')),
        cbk(v('mesAB')),
        Call(v('mesA'), F, DownMes(v('mesAB'))),
        Back()
      ],
      [
        Parse(UpMes(ret), v('mesA')),
      ]
    ])
  ]

def callCbk2(ret, F, mes, cbk1, cbk2):
  return lambda v: [
    Call(v('mesA'), F, UpMes(UpMes(mes))),
    Branches([
      [
        Parse(DownMes(v('mesAB')), v('mesA')),
        cbk1(v('mesAB')),
        Call(v('mesA'), F, DownMes(v('mesAB'))),
        Back()
      ],
      [
        Parse(UpMes(DownMes(v('mesAC'))), v('mesA')),
        cbk2(v('mesAC')),
        Call(v('mesA'), F, UpMes(DownMes(v('mesAC')))),
        Back()
      ],
      [
        Parse(UpMes(UpMes(ret)), v('mesA')),
      ]
    ])
  ]

composition2 = program(
  2,
  lambda v, F, G: [
    Message(v('mes')),
    callCbk(v('mes'), F, v('mes'), lambda m: Call(m, G, m)),
    Return(v('mes'))
  ]
).tighten()

