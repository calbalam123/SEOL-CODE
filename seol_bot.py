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


def _compile_command_body(body, economy_enabled):
    lines = []
    for statement in body:
        if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
            raise BotCompileError("명령어 블록에는 답장(), 계좌확인(), 잔액확인(), 송금처리()만 작성할 수 있습니다.")
        call = statement.value
        if not isinstance(call.func, ast.Name) or call.keywords:
            raise BotCompileError("지원하지 않는 명령어 블록 문법입니다.")
        name = call.func.id
        if name == "답장" and len(call.args) == 1:
            lines.append("            replier.reply(" + _js_expression(call.args[0]) + ");")
        elif name in ("계좌확인", "잔액확인", "송금처리") and not call.args:
            if not economy_enabled:
                raise BotCompileError("계좌 기능을 쓰려면 파일 맨 위에 경제시스템(시작잔액)을 먼저 작성하세요.")
            lines.append("            __seol_" + name + "(sender, msg, replier);")
        else:
            raise BotCompileError("명령어 블록에서는 답장(), 계좌확인(), 잔액확인(), 송금처리()를 사용할 수 있습니다.")
    if not lines:
        raise BotCompileError("명령어 블록에 실행할 내용을 한 개 이상 작성하세요.")
    return lines


def _economy_runtime(starting_balance):
    return r'''// 계좌 데이터는 휴대폰 내부 저장소의 JSON 파일에 보관됩니다.
var __seol_account_file = "/sdcard/SEOL_CODE_accounts.json";
function __seol_load_accounts() {
    try {
        var raw = FileStream.read(__seol_account_file);
        if (!raw) return {};
        var data = JSON.parse(raw);
        return data && typeof data === "object" ? data : {};
    } catch (e) { return {}; }
}
function __seol_save_accounts(data) {
    FileStream.write(__seol_account_file, JSON.stringify(data));
}
function __seol_get_account(sender, accounts) {
    var key = String(sender || "").trim();
    if (!key) return null;
    if (!accounts[key]) {
        accounts[key] = { balance: START_BALANCE };
        __seol_save_accounts(accounts);
    }
    return accounts[key];
}
function __seol_계좌확인(sender, msg, replier) {
    var accounts = __seol_load_accounts();
    var account = __seol_get_account(sender, accounts);
    if (!account) { replier.reply("발신자 정보를 읽을 수 없습니다."); return; }
    replier.reply("[ 설이은행 계좌 ]\n예금주: " + sender + "\n잔액: " + account.balance.toLocaleString() + "원");
}
function __seol_잔액확인(sender, msg, replier) {
    var accounts = __seol_load_accounts();
    var account = __seol_get_account(sender, accounts);
    if (!account) { replier.reply("발신자 정보를 읽을 수 없습니다."); return; }
    replier.reply("현재 잔액: " + account.balance.toLocaleString() + "원");
}
function __seol_송금처리(sender, msg, replier) {
    var parts = String(msg).trim().split(/\s+/);
    if (parts.length !== 3) {
        replier.reply("사용법: !송금 받는사람 금액\n예시: !송금 홍길동 1000");
        return;
    }
    var recipient = parts[1];
    var amount = Number(parts[2].replace(/,/g, ""));
    if (!isFinite(amount) || Math.floor(amount) !== amount || amount <= 0) {
        replier.reply("송금액은 1원 이상의 정수로 입력하세요.");
        return;
    }
    if (recipient === String(sender)) { replier.reply("자기 자신에게는 송금할 수 없습니다."); return; }
    var accounts = __seol_load_accounts();
    var from = __seol_get_account(sender, accounts);
    if (!from) { replier.reply("발신자 정보를 읽을 수 없습니다."); return; }
    var to = accounts[recipient];
    if (!to) { replier.reply("받는 사람이 아직 계좌를 만들지 않았습니다. 받는 사람이 먼저 !계좌를 입력해야 합니다."); return; }
    if (from.balance < amount) { replier.reply("잔액이 부족합니다. 현재 잔액: " + from.balance.toLocaleString() + "원"); return; }
    from.balance -= amount;
    to.balance += amount;
    __seol_save_accounts(accounts);
    replier.reply("송금 완료!\n받는 사람: " + recipient + "\n송금액: " + amount.toLocaleString() + "원\n남은 잔액: " + from.balance.toLocaleString() + "원");
}
'''.replace("START_BALANCE", str(starting_balance))


def compile_bot(source: str, filename: str = "<카카오봇>") -> str:
    try:
        tree = ast.parse(translate(source), filename=filename, mode="exec")
    except SyntaxError as exc:
        raise BotCompileError(f"{exc.lineno}번째 줄 문법 오류입니다. 괄호·콜론·들여쓰기를 확인하세요.") from None

    commands = []
    seen = set()
    starting_balance = None
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            if not isinstance(call.func, ast.Name) or call.func.id != "명령어":
                if isinstance(call.func, ast.Name) and call.func.id == "경제시스템":
                    if starting_balance is not None or len(call.args) != 1 or call.keywords:
                        raise BotCompileError("경제시스템()은 시작 잔액을 숫자 하나로 한 번만 설정하세요.")
                    value = call.args[0]
                    if not isinstance(value, ast.Constant) or not isinstance(value.value, int) or isinstance(value.value, bool) or value.value < 0:
                        raise BotCompileError("경제시스템()의 시작 잔액은 0 이상의 정수여야 합니다.")
                    starting_balance = value.value
                    continue
                raise BotCompileError("파일 최상위에는 경제시스템() 또는 명령어() 선언만 작성할 수 있습니다.")
            if len(call.args) != 2 or call.keywords:
                raise BotCompileError("고정 응답 형식은 명령어(명령, 응답) 문자열 2개가 필요합니다.")
            command = _string_arg(call.args[0], "명령어")
            reply = _string_arg(call.args[1], "응답")
            body = ["            replier.reply(" + json.dumps(reply, ensure_ascii=False) + ");"]
            is_prefix = False
        elif isinstance(node, ast.If):
            test = node.test
            if not (isinstance(test, ast.Call) and isinstance(test.func, ast.Name)
                    and test.func.id == "__seol_command__" and len(test.args) == 1
                    and not test.keywords):
                raise BotCompileError("명령어 블록은 명령어(\"!명령\"): 형식으로 시작해야 합니다.")
            command = _string_arg(test.args[0], "명령어")
            is_prefix = command == "!송금"
            body = _compile_command_body(node.body, starting_balance is not None)
            if node.orelse:
                raise BotCompileError("카카오봇 명령어 블록 안에서는 아직 아니면을 사용할 수 없습니다.")
        else:
            raise BotCompileError("파일 최상위에는 경제시스템() 또는 명령어() 선언만 작성할 수 있습니다.")

        if not command.strip():
            raise BotCompileError("명령어는 비워 둘 수 없습니다.")
        if command in seen:
            raise BotCompileError(f"'{command}' 명령어가 중복되었습니다.")
        seen.add(command)
        commands.append((command, body, is_prefix))

    if not commands:
        raise BotCompileError("명령어() 선언을 한 개 이상 작성하세요.")

    cases = []
    for command, body, is_prefix in commands:
        condition = ('String(msg).indexOf(' + json.dumps(command + " ", ensure_ascii=False) + ') === 0'
                     if is_prefix else 'msg === ' + json.dumps(command, ensure_ascii=False))
        cases.append("    if (" + condition + ") {\n" + "\n".join(body) + "\n    }")

    runtime = _economy_runtime(starting_balance) + "\n" if starting_balance is not None else ""
    return (runtime +
            "// 설이코드가 자동 생성한 MessengerBotR 연결 코드입니다.\n"
            "function response(room, msg, sender, isGroupChat, replier, imageDB, packageName) {\n"
            + "\n    else ".join(cases).replace("    if (", "    if (", 1) + "\n}\n")


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
