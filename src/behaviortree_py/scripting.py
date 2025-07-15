import ast
import operator as op
from typing import Any

from lark import Lark, Transformer, v_args


@v_args(inline=True)
class ScriptTransformer(Transformer):
    or_ = op.or_
    and_ = op.and_
    not_ = op.not_

    is_not = op.is_not
    is_ = op.is_
    le = op.le
    lt = op.lt
    gt = op.gt
    ge = op.ge
    ne = op.ne
    eq = op.eq

    add = op.add
    sub = op.sub
    mul = op.mul
    truediv = op.truediv
    floordiv = op.floordiv
    mod = op.mod

    neg = op.neg
    pow = op.pow

    int = int
    float = float

    def __init__(self, enums: dict[str, Any] | None = None):
        self.vars: dict[str, Any] = {}
        if enums is None:
            self.enums = {}
        else:
            self.enums = enums

    def state(self, *args):
        return args[-1]

    def assign(self, var, value):
        print(value)
        if var not in self.vars:
            raise NameError(f"{var} not found")
        self.vars[var] = value

    def define(self, var, value):
        self.vars[var] = value

    def var(self, value):
        if x := self.enums.get(value):
            return x
        return self.vars[value]

    def string(self, v):
        return ast.literal_eval(v)

    def true(self):
        return True

    def false(self):
        return False

    def none(self):
        return None


if __name__ == "__main__":
    from enum import Enum

    class NodeStatus(Enum):
        SUCCESS = 1
        FAILURE = 2
        RUNNING = 3
        IDLE = 4

    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    class Some(Enum):
        ABC = 3

    enums: dict[str, Any] = {s.name: s for s in NodeStatus}
    enums.update({s.name: s for s in Color})
    enums["THE_ANSWER"] = 42

    with open("grammar.lark", encoding="utf8") as grammar:
        parser = Lark(
            grammar.read(), parser="lalr", transformer=ScriptTransformer(enums)
        )
    calc = parser.parse

    for tree in (
        calc("A:=THE_ANSWER; B:=3.14; color:=RED"),
        calc("msg:='hello world'"),
        calc("A>B and color != BLUE"),
        calc("FAILURE"),
        calc("'hello'*2"),
    ):
        a = ScriptTransformer(enums).transform(tree)
        print(a)
