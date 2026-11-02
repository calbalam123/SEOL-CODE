#!/usr/bin/env python3
"""설이코드 카카오봇 선언을 MessengerBotR용 JavaScript로 변환합니다."""
import ast
import json
import sys
from pathlib import Path

from seol_language import translate


class BotCompileError(Exception):
    """카카오봇 선언을 변환할 수 없을 때 발생합니다."""


def _string_arg(node, label):
    if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
        raise BotCompileError(f"{label}은(는) 큰따옴표로 감싼 문자열이어야 합니다.")
    return node.value


def _js_expression(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return json.dumps(node.value, ensure_ascii=False)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return "(" + _js_expression(node.left) + " + " + _js_expression(node.right) + ")"
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.args and not node.keywords:
        names = {"보낸사람": "sender", "방이름": "room", "메시지": "msg"}
        if node.func.id in names:
            return names[node.func.id]
    raise BotCompileError("응답에는 문자열과 + 연산, 보낸사람(), 방이름(), 메시지()만 사용할 수 있습니다.")


def _compile_command_body(body):
    lines = []
    for statement in body:
        if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
            raise BotCompileError("명령어 블록에는 답장(\"응답\")만 작성할 수 있습니다.")
        call = statement.value
        if not isinstance(call.func, ast.Name) or call.func.id != "답장":
            raise BotCompileError("명령어 블록에서는 답장()을 사용하세요.")
        if len(call.args) != 1 or call.keywords:
            raise BotCompileError("답장()에는 응답 내용 하나를 넣어야 합니다.")
        lines.append("            replier.reply(" + _js_expression(call.args[0]) + ");")
    if not lines:
        raise BotCompileError("명령어 블록에 답장()을 한 개 이상 작성하세요.")
    return lines


def compile_bot(source: str, filename: str = "<카카오봇>") -> str:
    try:
        tree = ast.parse(translate(source), filename=filename, mode="exec")
    except SyntaxError as exc:
        raise BotCompileError(f"{exc.lineno}번째 줄 문법 오류입니다. 괄호·콜론·들여쓰기를 확인하세요.") from None

    commands = []
    seen = set()
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            if not isinstance(call.func, ast.Name) or call.func.id != "명령어":
                raise BotCompileError("명령어(\"!명령\", \"고정 응답\") 또는 명령어(\"!명령\"): 형식을 사용하세요.")
            if len(call.args) != 2 or call.keywords:
                raise BotCompileError("고정 응답 형식은 명령어(명령, 응답) 문자열 2개가 필요합니다.")
            command = _string_arg(call.args[0], "명령어")
            reply = _string_arg(call.args[1], "응답")
            body = ["            replier.reply(" + json.dumps(reply, ensure_ascii=False) + ");"]
        elif isinstance(node, ast.If):
            test = node.test
            if not (isinstance(test, ast.Call) and isinstance(test.func, ast.Name)
                    and test.func.id == "__seol_command__" and len(test.args) == 1
                    and not test.keywords):
                raise BotCompileError("명령어 블록은 명령어(\"!명령\"): 형식으로 시작해야 합니다.")
            command = _string_arg(test.args[0], "명령어")
            body = _compile_command_body(node.body)
            if node.orelse:
                raise BotCompileError("카카오봇 명령어 블록 안에서는 아직 아니면을 사용할 수 없습니다.")
        else:
            raise BotCompileError("파일 최상위에는 명령어() 선언만 작성할 수 있습니다.")

        if not command.strip():
            raise BotCompileError("명령어는 비워 둘 수 없습니다.")
        if command in seen:
            raise BotCompileError(f"'{command}' 명령어가 중복되었습니다.")
        seen.add(command)
        commands.append((command, body))

    if not commands:
        raise BotCompileError("명령어() 선언을 한 개 이상 작성하세요.")

    cases = []
    for command, body in commands:
        cases.append("        case " + json.dumps(command, ensure_ascii=False) + ":\n"
                     + "\n".join(body) + "\n            break;")

    return ("// 설이코드가 자동 생성한 MessengerBotR 연결 코드입니다.\n"
            "function response(room, msg, sender, isGroupChat, replier, imageDB, packageName) {\n"
            "    switch (msg) {\n" + "\n".join(cases) + "\n"
            "    }\n}\n")


def main() -> int:
    if len(sys.argv) != 3:
        print("사용법: python seol_bot.py 입력파일.seol 출력파일.js")
        return 2
    source_path, output_path = Path(sys.argv[1]), Path(sys.argv[2])
    try:
        source = source_path.read_text(encoding="utf-8")
        javascript = compile_bot(source, str(source_path))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(javascript, encoding="utf-8")
    except (OSError, BotCompileError) as exc:
        print(f"설이코드 카카오봇 오류: {exc}", file=sys.stderr)
        return 1
    print(f"카카오봇 연결 파일 생성 완료: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
