# 설이코드 VS Code 확장

## 기능
- .seol 파일 언어 인식 및 문법 색상 강조
- 괄호 자동 닫기와 들여쓰기
- 한국어 코드 조각
- F5로 현재 파일 실행
- 명령 팔레트에서 '설이코드: 현재 파일 실행'

## 설치
1. VS Code에서 SEOL-CODE 저장소 전체를 내려받고 압축을 풉니다.
2. VS Code에서 '파일 > 폴더 열기'로 SEOL-CODE 폴더를 엽니다.
3. Python 3.10 이상을 설치합니다.
4. 확장 기능은 VSIX 파일을 만들거나 VS Code 확장 개발 모드에서 이 폴더를 불러 설치할 수 있습니다.
5. .seol 파일을 열고 F5를 누릅니다.

## VSIX 설치
프로젝트 루트에서 아래 명령을 실행합니다.
```bash
npx --yes @vscode/vsce package --cwd vscode-extension
```
생성된 seol-code-0.3.0.vsix 파일을 VS Code 확장 탭의 ... 메뉴 > Install from VSIX...로 설치합니다.

## 설정
- `seol.pythonPath`: 기본값 `python`. Windows에서 Python Launcher를 쓰면 `py -3`로 설정할 수 있습니다.
- `seol.runnerPath`: seol.py 경로. 기본값은 현재 작업공간 최상위 폴더의 seol.py입니다.

중요: 확장 기능은 편집기 지원을 제공하고, 언어 실행기(seol.py 및 seol_language.py 등)는 SEOL-CODE 저장소에 있어야 합니다.
