#!/usr/bin/env python3
"""설이코드 0.2.0 명령줄 실행기."""
import sys
from pathlib import Path
from seol_language import Interpreter, SeolError, VERSION

def main():
    if len(sys.argv) > 2:
        print("사용법: python seol.py [파일.seol]")
        raise SystemExit(2)
    if len(sys.argv) == 2:
        path = Path(sys.argv[1])
        try:
            Interpreter().run(path.read_text(encoding="utf-8"), str(path))
        except (OSError, SeolError) as exc:
            print(f"설이코드 오류: {exc}", file=sys.stderr)
            raise SystemExit(1)
        return
    interpreter = Interpreter()
    print(f"설이코드 {VERSION} - 한국어 프로그래밍 시작!")
    print("한 줄 코드를 입력하세요. 종료하려면 '종료'를 입력하세요.")
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
