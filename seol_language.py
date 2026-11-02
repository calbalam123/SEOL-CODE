"""설이코드 0.2.0 확장 인터프리터."""
import ast
import operator
from seol_builtins import BUILTINS

VERSION = "0.3.0"
OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
       ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
       ast.Mod: operator.mod, ast.Pow: operator.pow}
CMPS = {ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt,
        ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge,
        ast.In: lambda a,b: a in b, ast.NotIn: lambda a,b: a not in b}

class SeolError(Exception): pass
class Returned(Exception):
    def __init__(self, value): self.value = value
class Function:
    def __init__(self, name, args, body, closure):
        self.name, self.args, self.body, self.closure = name, args, body, closure

def translate(source):
    lines = []
    for line in source.splitlines():
        s = line.lstrip()
        indent = line[:len(line)-len(s)]
        if not s or s.startswith("#"):
            lines.append(line); continue
        if s.startswith("만약 ") and s.endswith(":"): s = "if " + s[3:]
        elif s == "아니면:": s = "else:"
        elif s.startswith("반복 ") and s.endswith("회:"):
            s = "for __seol_index in range(" + s[3:-2].strip() + "):"
        elif s.startswith("반복 ") and " in " in s and s.endswith(":"): s = "for " + s[3:]
        elif s.startswith("함수 ") and s.endswith(":"): s = "def " + s[3:]
        elif s.startswith("반환"): s = "return" + ((" " + s[2:].strip()) if s[2:].strip() else "")
        s = s.replace(" 그리고 ", " and ").replace(" 또는 ", " or ")
        if s.startswith("아니다 "): s = "not " + s[4:]
        lines.append(indent+s)
    return "\n".join(lines)

class Interpreter:
    def __init__(self):
        self.env = {"참": True, "거짓": False, "없음": None,
          "출력": self._print, "길이": len, "문자열": str, "정수": int, "실수": float,
          "반올림": round, "절댓값": abs, "최댓값": max, "최솟값": min, "합계": sum,
          "추가": self._append, "포함": lambda a,b: b in a}
        self.env.update(BUILTINS)
        self.depth = 0
        self.max_loop = 100000
    @staticmethod
    def _print(*args): print(*args)
    @staticmethod
    def _append(items, value):
        if not isinstance(items, list): raise SeolError("추가()의 첫 번째 값은 목록이어야 합니다.")
        items.append(value); return items
    def run(self, source, filename="<입력>"):
        try: tree = ast.parse(translate(source), filename=filename, mode="exec")
        except SyntaxError as e: raise SeolError(f"{e.lineno}번째 줄 문법 오류입니다. 괄호·콜론·들여쓰기를 확인하세요.") from None
        try: self.block(tree.body, self.env)
        except Returned: raise SeolError("반환은 함수 안에서만 사용할 수 있습니다.")
        except SeolError: raise
        except Exception as e: raise SeolError(f"실행 중 오류: {e}") from None
    def block(self, nodes, env):
        for n in nodes: self.statement(n, env)
    def assign(self, target, value, env):
        if isinstance(target, ast.Name): env[target.id] = value
        elif isinstance(target, ast.Subscript): self.value(target.value,env)[self.value(target.slice,env)] = value
        else: raise SeolError("변수 또는 목록 위치에만 값을 저장할 수 있습니다.")
    def statement(self, n, env):
        if isinstance(n, ast.Assign):
            v=self.value(n.value,env)
            for t in n.targets: self.assign(t,v,env)
        elif isinstance(n, ast.AugAssign):
            if not isinstance(n.target,ast.Name) or type(n.op) not in OPS: raise SeolError("이 값 변경 문법은 지원하지 않습니다.")
            env[n.target.id]=OPS[type(n.op)](self.value(n.target,env),self.value(n.value,env))
        elif isinstance(n, ast.Expr): self.value(n.value,env)
        elif isinstance(n, ast.If): self.block(n.body if self.value(n.test,env) else n.orelse,env)
        elif isinstance(n, ast.For):
            if not isinstance(n.target,ast.Name): raise SeolError("반복 변수는 이름 하나여야 합니다.")
            if isinstance(n.iter,ast.Call) and isinstance(n.iter.func,ast.Name) and n.iter.func.id=="range":
                args=[self.value(a,env) for a in n.iter.args]
                if len(args)!=1 or not isinstance(args[0],int): raise SeolError("반복 횟수는 정수 하나여야 합니다.")
                seq=range(args[0])
            else: seq=self.value(n.iter,env)
            if not isinstance(seq,(list,tuple,str,dict,range)): raise SeolError("반복 대상은 목록·문자열·사전이어야 합니다.")
            if len(seq)>self.max_loop: raise SeolError("반복 횟수가 너무 큽니다.")
            for x in seq: env[n.target.id]=x; self.block(n.body,env)
        elif isinstance(n,ast.FunctionDef):
            if n.args.defaults or n.args.vararg or n.args.kwarg or n.args.kwonlyargs: raise SeolError("기본값 없는 일반 매개변수만 지원합니다.")
            env[n.name]=Function(n.name,[a.arg for a in n.args.args],n.body,env)
        elif isinstance(n,ast.Return): raise Returned(self.value(n.value,env) if n.value else None)
        elif isinstance(n,ast.Pass): return
        else: raise SeolError(f"지원하지 않는 문장: {type(n).__name__}")
    def value(self,n,env):
        if isinstance(n,ast.Constant): return n.value
        if isinstance(n,ast.Name):
            if n.id not in env: raise SeolError(f"'{n.id}' 변수를 찾을 수 없습니다.")
            return env[n.id]
        if isinstance(n,ast.BinOp) and type(n.op) in OPS:
            a,b=self.value(n.left,env),self.value(n.right,env)
            if isinstance(n.op,ast.Pow) and abs(b)>1000: raise SeolError("거듭제곱 지수가 너무 큽니다.")
            return OPS[type(n.op)](a,b)
        if isinstance(n,ast.UnaryOp):
            v=self.value(n.operand,env)
            if isinstance(n.op,ast.USub): return -v
            if isinstance(n.op,ast.UAdd): return +v
            if isinstance(n.op,ast.Not): return not v
        if isinstance(n,ast.BoolOp):
            vals=[self.value(x,env) for x in n.values]
            return all(vals) if isinstance(n.op,ast.And) else any(vals)
        if isinstance(n,ast.Compare):
            left=self.value(n.left,env)
            for op,part in zip(n.ops,n.comparators):
                right=self.value(part,env)
                if type(op) not in CMPS or not CMPS[type(op)](left,right): return False
                left=right
            return True
        if isinstance(n,ast.IfExp): return self.value(n.body if self.value(n.test,env) else n.orelse,env)
        if isinstance(n,ast.Call):
            if not isinstance(n.func,ast.Name): raise SeolError("함수 이름으로만 호출할 수 있습니다.")
            name=n.func.id
            if name=="range": raise SeolError("반복문 안에서만 사용할 수 있습니다.")
            fn=env.get(name)
            if fn is None: raise SeolError(f"'{name}' 함수를 찾을 수 없습니다.")
            args=[self.value(x,env) for x in n.args]
            if isinstance(fn,Function):
                if len(args)!=len(fn.args): raise SeolError(f"{name} 함수의 매개변수 개수가 맞지 않습니다.")
                if self.depth>=100: raise SeolError("함수 호출이 너무 깊습니다.")
                local=dict(fn.closure); local.update(zip(fn.args,args)); self.depth+=1
                try:
                    self.block(fn.body,local)
                except Returned as r: return r.value
                finally: self.depth-=1
                return None
            if callable(fn): return fn(*args)
            raise SeolError(f"'{name}'은(는) 함수가 아닙니다.")
        if isinstance(n,ast.List): return [self.value(x,env) for x in n.elts]
        if isinstance(n,ast.Tuple): return tuple(self.value(x,env) for x in n.elts)
        if isinstance(n,ast.Dict): return {self.value(k,env):self.value(v,env) for k,v in zip(n.keys,n.values)}
        if isinstance(n,ast.Subscript): return self.value(n.value,env)[self.value(n.slice,env)]
        if isinstance(n,ast.Slice):
            return slice(self.value(n.lower,env) if n.lower else None,self.value(n.upper,env) if n.upper else None,self.value(n.step,env) if n.step else None)
        raise SeolError(f"지원하지 않는 표현식: {type(n).__name__}")
