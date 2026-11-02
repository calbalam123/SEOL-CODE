#!/usr/bin/env python3
"""설이코드 카카오봇 선언을 MessengerBotR용 JavaScript로 변환합니다.

설이코드 사용자는 .seol 파일만 작성하고, 이 도구가 MessengerBotR
호환 어댑터 코드를 생성합니다. 생성된 어댑터는 MessengerBotR에서 실행됩니다.
"""
import ast
import json
import sys
from pathlib import Path

from seol_language import translate


class BotCompileError(Exception):
    """카카오봇 선언을 변환할 수 없을 때 발생합니다."""


def compile_bot(source: str, filename: str = "<카카오봇>") -> str:
    """명령어("!명령", "응답") 선언을 MessengerBotR 스크립트로 변환합니다."""
    try:
        tree = ast.parse(translate(source), filename=filename, mode="exec")
    except SyntaxError as exc:
        raise BotCompileError(
            f"{exc.lineno}번째 줄 문법 오류입니다. 괄호와 따옴표를 확인하세요."
        ) from None

    commands = []
    seen = set()

    for node in tree.body:
        if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
            raise BotCompileError(
                "카카오봇 첫 버전에서는 명령어(\"!명령\", \"응답\") 형식만 사용할 수 있습니다."
            )

        call = node.value
        if not isinstance(call.func, ast.Name) or call.func.id != "명령어":
            raise BotCompileError(
                "지원하지 않는 선언입니다. 명령어(\"!명령\", \"응답\")를 사용하세요."
            )
        if len(call.args) != 2 or call.keywords:
            raise BotCompileError(
                "명령어()에는 명령어와 응답 문장, 문자열 2개를 넣어야 합니다."
            )
        if not all(isinstance(arg, ast.Constant) and isinstance(arg.value, str)
                   for arg in call.args):
            raise BotCompileError("명령어와 응답은 큰따옴표로 감싼 문자열이어야 합니다.")

        command, reply = (arg.value for arg in call.args)
        if not command.strip():
            raise BotCompileError("명령어는 비워 둘 수 없습니다.")
        if command in seen:
            raise BotCompileError(f"'{command}' 명령어가 중복되었습니다.")
        seen.add(command)
        commands.append((command, reply))

    if not commands:
        raise BotCompileError("명령어() 선언을 한 개 이상 작성하세요.")

    cases = []
    for command, reply in commands:
        cases.append(
            "        case " + json.dumps(command, ensure_ascii=False) + ":\n"
            "            replier.reply(" + json.dumps(reply, ensure_ascii=False) + ");\n"
            "            break;"
        )

    return (
        "// 설이코드가 자동 생성한 MessengerBotR 연결 코드입니다.\n"
        "// 원본 .seol 파일을 수정한 뒤 다시 생성할 수 있습니다.\n"
        "function response(room, msg, sender, isGroupChat, replier, imageDB, packageName) {\n"
        "    switch (msg) {\n"
        + "\n".join(cases) + "\n"
        "    }\n"
        "}\n"
    )


def main() -> int:
    if len(sys.argv) != 3:
        print("사용법: python seol_bot.py 입력파일.seol 출력파일.js")
        return 2
    source_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
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
