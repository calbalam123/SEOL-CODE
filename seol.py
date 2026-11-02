#!/usr/bin/env python3
"""설이코드(SEOL CODE) 0.1.0 - 한국어 문법 학습용 인터프리터."""

from __future__ import annotations

import ast
import operator
import sys
from pathlib import Path
from typing import Any


VERSION = "0.1.0"

_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_COMPARE = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}


class SeolError(Exception):
    """사용자에게 보여 줄 설이코드 오류."""


class ReturnSignal(Exception):
    def __init__(self, value: Any):
        self.value = value


class UserFunction:
    def __init__(self, name: str, parameters: list[str], body: list[ast.stmt], closure: dict):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.closure = closure


def translate(source: str) -> str:
    """설이코드의 한국어 키워드를 Python 문법 트리용 표기로 바꿉니다."""
    converted = []
    for line_number, original in enumerate(source.splitlines(), 1):
        stripped = original.lstrip()
        indent = original[: len(original) - len(stripped)]
        if not stripped or stripped.startswith("#"):
            converted.append(original)
            continue

        if stripped.startswith("만약 ") and stripped.endswith(":"):
            stripped = "if " + stripped[3:]
        elif stripped == "아니면:":
            stripped = "else:"
        elif stripped.startswith("반복 ") and stripped.endswith(":") and stripped.endswith("회:"):
            count = stripped[len("반복 "):-len("회:")].strip()
            stripped = f"for __seol_index in range({count}):"
        elif stripped.startswith("함수 ") and stripped.endswith(":"):
            stripped = "def " + stripped[len("함수 "):]
        elif stripped.startswith("반환"):
            rest = stripped[len("반환"):].strip()
            stripped = "return" + ((" " + rest) if rest else "")
        stripped = stripped.replace(" 그리고 ", " and ").replace(" 또는 ", " or ")
        if stripped.startswith("아니다 "):
            stripped = "not " + stripped[len("아니다 "):]
        converted.append(indent + stripped)

    return "\n".join(converted)


class Interpreter:
    def __init__(self):
        self.globals: dict[str, Any] = {
            "참": True,
            "거짓": False,
            "없음": None,
            "출력": self._print,
            "길이": len,
            "문자열": str,
            "정수": int,
            "실수": float,
        }
        self.max_loop = 100_000
        self.call_depth = 0

    @staticmethod
    def _print(*values):
        print(*values)

    def run(self, source: str, filename: str = "<입력>"):
        try:
            translated = translate(source)
            tree = ast.parse(translated, filename=filename, mode="exec")
            self._exec_block(tree.body, self.globals)
        except SyntaxError as exc:
            line = exc.lineno or "?"
            raise SeolError(
                f"{line}번째 줄 문법을 확인해 주세요. 콜론(:)과 들여쓰기를 확인하세요."
            ) from None
        except SeolError:
            raise
        except Exception as exc:
            raise SeolError(f"실행 중 오류가 발생했습니다: {exc}") from None

    def _exec_block(self, statements: list[ast.stmt], env: dict):
        for node in statements:
            self._exec_statement(node, env)

    def _exec_statement(self, node: ast.stmt, env: dict):
        if isinstance(node, ast.Assign):
            value = self._eval(node.value, env)
            for target in node.targets:
                if not isinstance(target, ast.Name):
                    raise SeolError("변수 이름에만 값을 저장할 수 있습니다.")
                env[target.id] = value
        elif isinstance(node, ast.Expr):
            self._eval(node.value, env)
        elif isinstance(node, ast.If):
            branch = node.body if self._eval(node.test, env) else node.orelse
            self._exec_block(branch, env)
        elif isinstance(node, ast.For):
            if not isinstance(node.target, ast.Name) or not isinstance(node.iter, ast.Call):
                raise SeolError("'반복 숫자회:' 형식을 사용해 주세요.")
            if not isinstance(node.iter.func, ast.Name) or node.iter.func.id != "range":
                raise SeolError("반복 횟수는 숫자로 지정해 주세요.")
            args = [self._eval(arg, env) for arg in node.iter.args]
            if len(args) != 1 or not isinstance(args[0], int):
                raise SeolError("반복 횟수는 정수 하나여야 합니다.")
            if args[0] < 0 or args[0] > self.max_loop:
                raise SeolError(f"반복 횟수는 0~{self.max_loop} 사이여야 합니다.")
            for index in range(args[0]):
                env[node.target.id] = index
                self._exec_block(node.body, env)
        elif isinstance(node, ast.FunctionDef):
            params = []
            for arg in node.args.args:
                params.append(arg.arg)
            if node.args.vararg or node.args.kwarg or node.args.kwonlyargs or node.args.defaults:
                raise SeolError("현재 함수는 기본값 없는 일반 매개변수만 지원합니다.")
            env[node.name] = UserFunction(node.name, params, node.body, env)
        elif isinstance(node, ast.Return):
            raise ReturnSignal(self._eval(node.value, env) if node.value else None)
        elif isinstance(node, ast.Pass):
            return
        else:
            raise SeolError(f"아직 지원하지 않는 문법입니다: {type(node).__name__}")

    def _eval(self, node: ast.AST, env: dict):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (str, int, float, bool)) or node.value is None:
                return node.value
            raise SeolError("지원하지 않는 값입니다.")
        if isinstance(node, ast.Name):
            if node.id in env:
                return env[node.id]
            raise SeolError(f"'{node.id}' 변수를 찾을 수 없습니다.")
        if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
            left, right = self._eval(node.left, env), self._eval(node.right, env)
            if isinstance(node.op, ast.Pow) and abs(right) > 1000:
                raise SeolError("거듭제곱 지수가 너무 큽니다.")
            return _BINARY[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp):
            value = self._eval(node.operand, env)
            if isinstance(node.op, ast.USub):
                return -value
            if isinstance(node.op, ast.UAdd):
                return +value
            if isinstance(node.op, ast.Not):
                return not value
        if isinstance(node, ast.Compare):
            left = self._eval(node.left, env)
            for op, comparator in zip(node.ops, node.comparators):
                right = self._eval(comparator, env)
                if type(op) not in _COMPARE or not _COMPARE[type(op)](left, right):
                    return False
                left = right
            return True
        if isinstance(node, ast.BoolOp):
            values = [self._eval(value, env) for value in node.values]
            if isinstance(node.op, ast.And):
                return all(values)
            if isinstance(node.op, ast.Or):
                return any(values)
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise SeolError("함수 이름으로만 호출할 수 있습니다.")
            name = node.func.id
            if name == "range":
                raise SeolError("'range'는 직접 사용할 수 없습니다. '반복 숫자회:'를 사용하세요.")
            function = env.get(name)
            if function is None:
                raise SeolError(f"'{name}' 함수를 찾을 수 없습니다.")
            args = [self._eval(arg, env) for arg in node.args]
            if isinstance(function, UserFunction):
                if len(args) != len(function.parameters):
                    raise SeolError(
                        f"'{name}' 함수에는 매개변수 {len(function.parameters)}개가 필요합니다."
                    )
                if self.call_depth >= 100:
                    raise SeolError("함수 호출이 너무 깊습니다.")
                local = dict(function.closure)
                local.update(zip(function.parameters, args))
                self.call_depth += 1
                try:
                    self._exec_block(function.body, local)
                except ReturnSignal as signal:
                    return signal.value
                finally:
                    self.call_depth -= 1
                return None
            if callable(function) and name in {"출력", "길이", "문자열", "정수", "실수"}:
                return function(*args)
            raise SeolError(f"'{name}' 함수는 호출할 수 없습니다.")
        if isinstance(node, ast.List):
            return [self._eval(item, env) for item in node.elts]
        raise SeolError(f"지원하지 않는 표현식입니다: {type(node).__name__}")


def main():
    interpreter = Interpreter()
    if len(sys.argv) > 2:
        print("사용법: python seol.py [파일.seol]")
        raise SystemExit(2)
    if len(sys.argv) == 2:
        path = Path(sys.argv[1])
        try:
            source = path.read_text(encoding="utf-8")
            interpreter.run(source, str(path))
        except OSError as exc:
            print(f"파일을 열 수 없습니다: {exc}", file=sys.stderr)
            raise SystemExit(1)
        except SeolError as exc:
            print(f"설이코드 오류: {exc}", file=sys.stderr)
            raise SystemExit(1)
        return

    print(f"설이코드 {VERSION} - 한국어 프로그래밍 시작!")
    print("코드를 입력하고 Ctrl+C로 종료하세요. (여러 줄 블록은 .seol 파일 실행을 권장합니다.)")
    while True:
        try:
            line = input("설이> ")
            if line.strip() in {"종료", "끝"}:
                break
            interpreter.run(line)
        except KeyboardInterrupt:
            print("\n설이코드를 종료합니다.")
            break
        except SeolError as exc:
            print(f"설이코드 오류: {exc}")


if __name__ == "__main__":
    main()
