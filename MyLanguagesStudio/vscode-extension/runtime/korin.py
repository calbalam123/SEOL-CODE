"""Korin runtime bundled for VS Code extension."""
from pathlib import Path
import sys, re, traceback, json
from nexadb import NexaDB
KEYWORDS=[(r'\b변수\s+',''),(r'\b출력\s*\(','print('),(r'\b입력\s*\(','input('),(r'\b참\b','True'),(r'\b거짓\b','False'),(r'\b없음\b','None'),(r'\b그리고\b','and'),(r'\b또는\b','or'),(r'\b아님\b','not'),(r'\b함수\s+','def '),(r'\b반환\b','return'),(r'\b아니면\s+만약\s+','elif '),(r'\b만약\s+','if '),(r'\b아니면\b','else'),(r'\b동안\s+','while '),(r'\b각각\s+','for '),(r'\b범위\s*\(','range('),(r'\b클래스\s+','class '),(r'\b가져오기\s+','import '),(r'\b에서\s+','from ')]
def translate(src):
 out=[]
 for line in src.splitlines():
  if not line.strip() or line.strip().startswith("#"): out.append(line); continue
  chunks=re.split(r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')',line)
  for i in range(0,len(chunks),2):
   for pat,repl in KEYWORDS: chunks[i]=re.sub(pat,repl,chunks[i])
  out.append("".join(chunks))
 return "\n".join(out)
class KorinDB:
 def __init__(self,f): self.db=NexaDB(f)
 def 실행(self,s,p=()): return self.db.execute(s,p).rowcount
 def 조회(self,s,p=()): return self.db.query(s,p)
 def 테이블목록(self): return self.db.tables()
 def 닫기(self): self.db.close()
def run_file(f):
 path=Path(f).resolve()
 def dbopen(n):
  p=Path(n); return KorinDB(p if p.is_absolute() else (path.parent/p).resolve())
 ns={"__name__":"__main__","데이터베이스":dbopen,"NexaDB":dbopen,"JSON":json}
 try: exec(compile(translate(path.read_text(encoding="utf-8-sig")),str(path),"exec"),ns,ns)
 except Exception: traceback.print_exc(); raise SystemExit(1)
def build_web(project,out=None):
 project=Path(project).resolve(); out=Path(out).resolve() if out else project/"dist"; out.mkdir(parents=True,exist_ok=True)
 mp={".khtml":".html",".kcss":".css",".kjs":".js"}
 for f in project.rglob("*"):
  if f.is_file() and f.suffix in mp and "dist" not in f.parts:
   t=out/f.relative_to(project).with_suffix(mp[f.suffix]); t.parent.mkdir(parents=True,exist_ok=True); t.write_text(f.read_text(encoding="utf-8-sig"),encoding="utf-8")
 print("[Korin] 웹 빌드 완료:",out)
if __name__=="__main__":
 if len(sys.argv)<3: raise SystemExit("사용법: korin.py 실행 파일.k | 웹빌드 프로젝트")
 if sys.argv[1]=="실행": run_file(sys.argv[2])
 elif sys.argv[1]=="웹빌드": build_web(sys.argv[2],sys.argv[3] if len(sys.argv)>3 else None)
