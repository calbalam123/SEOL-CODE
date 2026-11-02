# 설이코드 VS Code 확장 (독립 실행형)

## 기능
- `.seol` 파일 자동 인식 및 문법 색상 강조
- 괄호 자동 닫기와 들여쓰기
- 한국어 코드 조각
- 편집기 오른쪽 위 ▶ 실행 버튼 및 F5 실행
- 실행 결과는 VS Code 통합 터미널에 표시
- Windows x64용 설이코드 실행기(EXE)를 확장에 포함

## 설치 및 사용
1. GitHub 저장소의 Actions에서 **SeolCode-Standalone-VSCode-Extension** 아티팩트를 내려받습니다.
2. ZIP 압축을 풀어 안에 있는 `.vsix` 파일을 찾습니다.
3. VS Code 확장 탭의 ... 메뉴 > **Install from VSIX...** 에서 해당 파일을 선택합니다.
4. VS Code를 다시 로드합니다.
5. 아무 폴더나 열고 `.seol` 파일을 만든 뒤 ▶ 또는 F5로 실행합니다.

## 독립 실행형 안내
이 확장 패키지에는 Windows x64용 설이코드 인터프리터 실행 파일이 포함됩니다. 사용자는 별도로 Python을 설치하거나 `seol.py`를 준비할 필요가 없습니다. 실행기 코드는 프로젝트의 `seol.py`, `seol_language.py`, `seol_builtins.py`를 PyInstaller로 묶어 빌드합니다.

현재 제공 대상은 Windows x64입니다. 다른 운영체제용 확장 패키지는 별도 빌드가 필요합니다.
