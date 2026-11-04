# MyLanguages Studio — Korin + NexaDB

한국어 우선 통합 개발 환경 초기 버전.

## 구성
- `.db`: 실제 SQLite 데이터베이스 파일
- `.nql`: NexaDB 한국어 데이터베이스 명령 스크립트
- `.k`: Korin 한국어 프로그래밍 언어
- `.khtml`, `.kcss`, `.kjs`: 웹 프로젝트 파일
- `vscode-extension/`: VS Code 문법 강조, 스니펫, 파일 아이콘, 실행 명령 확장

## 준비물
Windows 10/11, Python 3.10 이상, VS Code 1.80 이상.

## 실행
저장소 루트에서:
- NexaDB: `python MyLanguagesStudio/runtime/nexadb_cli.py MyLanguagesStudio/examples/NexaDB/학교.nql`
- Korin: `python MyLanguagesStudio/runtime/korin.py 실행 MyLanguagesStudio/examples/Korin/안녕.k`
- DB 연동: NexaDB 스크립트를 먼저 실행한 뒤 `python MyLanguagesStudio/runtime/korin.py 실행 MyLanguagesStudio/examples/Korin/데이터베이스연동.k`
- 웹 빌드: `python MyLanguagesStudio/runtime/korin.py 웹빌드 MyLanguagesStudio/examples/Web`

## 주의
NexaDB는 SQLite 엔진/파일 형식을 사용하며 독립 저장 엔진이나 네트워크 서버는 아닙니다. Korin은 한국어 키워드를 Python 구문으로 변환하는 초기 실행기입니다. 웹 자산은 HTML/CSS/JavaScript 표준 문법으로 작성합니다.
