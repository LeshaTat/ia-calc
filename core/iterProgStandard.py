from core.iterProg import *

def lib(ret, F, mes):
  return lambda v: [
    Call(ret, F, mes),
  ]

def mem(ret, k, mes):
  return lambda v: [
    Call(ret, k, mes, mem=True),
  ]

composition = program(
  2,
  lambda v, F, G: [
    Message(v('mes')),
    Call(v('mesA'), F, Up(v('mes'))),
    Branches([
      [
        Parse(Down(v('mesAB')), v('mesA')),
        Call(v('mesBA'), G, v('mesAB')),
        Call(v('mesA'), F, Down(v('mesBA'))),
        Back()
      ],
      [
        Parse(Up(v('mes')), v('mesA')),
        Return(v('mes'))
      ]
    ])
  ]
).tighten()

def callCbk(ret, F, mes, cbk):
  return lambda v: [
    Call(v('mesA'), F, Up(mes)),
    Branches([
      [
        Parse(Down(v('mesAB')), v('mesA')),
        Set(v('mesA'), c0),
        cbk(v('mesAB')),
        Call(v('mesA'), F, Down(v('mesAB'))),
        Back()
      ],
      [
        Parse(Up(ret), v('mesA')),
        Set(v('mesAB'), c0)
      ]
    ])
  ]

def callCbk2(ret, F, mes, cbk1, cbk2):
  return lambda v: [
    Call(v('mesA'), F, Up(Up(mes))),
    Branches([
      [
        Parse(Down(v('mesAB')), v('mesA')),
        Set(v('mesA'), c0),
        Set(v('mesAC'), c0),
        cbk1(v('mesAB')),
        Call(v('mesA'), F, Down(v('mesAB'))),
        Back()
      ],
      [
        Parse(Up(Down(v('mesAC'))), v('mesA')),
        Set(v('mesA'), c0),
        Set(v('mesAB'), c0),
        cbk2(v('mesAC')),
        Call(v('mesA'), F, Up(Down(v('mesAC')))),
        Back()
      ],
      [
        Parse(Up(Up(ret)), v('mesA')),
        Set(v('mesAC'), c0),
        Set(v('mesAB'), c0)
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

