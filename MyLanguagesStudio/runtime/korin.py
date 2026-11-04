"""Korin: Korean-first language runtime."""
from pathlib import Path
import sys, re, traceback, json
from nexadb import NexaDB

KEYWORDS = [
    (r'\b변수\s+', ''), (r'\b출력\s*\(', 'print('), (r'\b입력\s*\(', 'input('),
    (r'\b참\b', 'True'), (r'\b거짓\b', 'False'), (r'\b없음\b', 'None'),
    (r'\b그리고\b', 'and'), (r'\b또는\b', 'or'), (r'\b아님\b', 'not'),
    (r'\b함수\s+', 'def '), (r'\b반환\b', 'return'),
    (r'\b아니면\s+만약\s+', 'elif '), (r'\b만약\s+', 'if '), (r'\b아니면\b', 'else'),
    (r'\b동안\s+', 'while '), (r'\b각각\s+', 'for '), (r'\b범위\s*\(', 'range('),
    (r'\b클래스\s+', 'class '), (r'\b가져오기\s+', 'import '), (r'\b에서\s+', 'from '),
    (r'\b시도\b', 'try:'), (r'\b예외\b', 'except Exception:'), (r'\b마지막\b', 'finally:'),
    (r'\b발생\s+', 'raise '), (r'\b중단\b', 'break'), (r'\b계속\b', 'continue'), (r'\b통과\b', 'pass')
]
def translate(source):
    result=[]
    for line in source.replace("\r","").splitlines():
        if not line.strip() or line.strip().startswith("#"):
            result.append(line); continue
        chunks=re.split(r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')',line)
        for i in range(0,len(chunks),2):
            for pat,repl in KEYWORDS: chunks[i]=re.sub(pat,repl,chunks[i])
        result.append("".join(chunks))
    return "\n".join(result)

class KorinDB:
    def __init__(self, filename): self.db=NexaDB(filename)
    def 실행(self, sql, params=()): return self.db.execute(sql,params).rowcount
    def 조회(self, sql, params=()): return self.db.query(sql,params)
    def 테이블목록(self): return self.db.tables()
    def 닫기(self): self.db.close()

def run_file(filename):
    path=Path(filename).resolve()
    def open_db(name):
        p=Path(name)
        return KorinDB(p if p.is_absolute() else (path.parent/p).resolve())
    namespace={"__name__":"__main__","__file__":str(path),"데이터베이스":open_db,"NexaDB":open_db,"JSON":json,"경로":str}
    try: exec(compile(translate(path.read_text(encoding="utf-8-sig")),str(path),"exec"),namespace,namespace)
    except Exception: traceback.print_exc(); raise SystemExit(1)

def build_web(project_dir, output_dir=None):
    project=Path(project_dir).resolve(); out=Path(output_dir).resolve() if output_dir else project/"dist"
    out.mkdir(parents=True,exist_ok=True)
    mapping={".khtml":".html",".kcss":".css",".kjs":".js"}
    for f in project.rglob("*"):
        if f.is_file() and not any(x in ("dist",".venv","__pycache__") for x in f.parts) and f.suffix in mapping:
            target=out/f.relative_to(project).with_suffix(mapping[f.suffix]); target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(f.read_text(encoding="utf-8-sig"),encoding="utf-8")
    print(f"[Korin] 웹 빌드 완료: {out}")

if __name__=="__main__":
    if len(sys.argv)<3: print("사용법: korin.py 실행 파일.k | 웹빌드 프로젝트폴더"); raise SystemExit(2)
    if sys.argv[1]=="실행": run_file(sys.argv[2])
    elif sys.argv[1]=="웹빌드": build_web(sys.argv[2],sys.argv[3] if len(sys.argv)>3 else None)
    else: raise SystemExit("알 수 없는 작업")
