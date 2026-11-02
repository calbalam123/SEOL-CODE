# 설이코드 VS Code 확장

## 기능
- .seol 파일 자동 인식 및 문법 색상 강조
- 괄호 자동 닫기와 들여쓰기
- 한국어 코드 조각
- 편집기 오른쪽 위의 ▶ 실행 버튼
- F5 또는 명령 팔레트의 '설이코드: 현재 파일 실행'
- 실행 결과는 VS Code 통합 터미널에 표시

## 설치 및 사용
1. SEOL-CODE 저장소 전체 폴더를 내려받아 압축을 풉니다.
2. VS Code에서 **파일 > 폴더 열기**로 SEOL-CODE 폴더를 엽니다. 최상위 폴더에 `seol.py`가 있어야 합니다.
3. Python 3.10 이상을 설치합니다.
4. GitHub Actions에서 `SeolCode-VSCode-Extension` 아티팩트를 내려받아 ZIP을 풉니다.
5. VS Code 확장 탭의 ... 메뉴 > **Install from VSIX...** 에서 `.vsix` 파일을 선택합니다.
6. VS Code를 다시 로드한 뒤 `.seol` 파일을 엽니다.
7. 편집기 오른쪽 위 ▶ 버튼 또는 F5를 눌러 실행합니다.

## 설정
- `seol.pythonPath`: 기본값 `python`. Python Launcher를 쓰는 경우 `py`로 설정할 수 있습니다.
- `seol.runnerPath`: `seol.py` 실행기 경로. 기본값은 열려 있는 작업공간 최상위 폴더의 `seol.py`입니다.

참고: 확장 프로그램은 VS Code 편집기 기능을 제공하며, 실제 실행은 저장소의 Python 실행기(`seol.py` 및 관련 파일)를 사용합니다. Python은 설치되어 있어야 합니다.
