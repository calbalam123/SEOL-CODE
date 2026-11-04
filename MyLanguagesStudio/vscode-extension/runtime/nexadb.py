"""NexaDB SQLite runtime bundled with Korin."""
import sqlite3, re, json
from pathlib import Path

class NexaDB:
 def __init__(self,filename):
  self.filename=str(Path(filename).resolve())
  self.conn=sqlite3.connect(self.filename)
  self.conn.row_factory=sqlite3.Row
  self.conn.execute("PRAGMA foreign_keys=ON")
 def close(self): self.conn.close()
 def execute(self,sql,params=()):
  cur=self.conn.execute(sql,params); self.conn.commit(); return cur
 def query(self,sql,params=()): return [dict(r) for r in self.conn.execute(sql,params).fetchall()]
 def tables(self): return [r["name"] for r in self.query("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
 def begin(self): self.conn.execute("BEGIN")
 def commit(self): self.conn.commit()
 def rollback(self): self.conn.rollback()

def split_values(s):
 out=[]; cur=""; quote=None
 for c in s:
  if quote:
   cur+=c
   if c==quote: quote=None
  elif c in ("'",'"'): quote=c; cur+=c
  elif c==",": out.append(cur.strip()); cur=""
  else: cur+=c
 if cur.strip(): out.append(cur.strip())
 return out

def run_script(filename):
 db=None
 try:
  for no,raw in enumerate(Path(filename).read_text(encoding="utf-8-sig").splitlines(),1):
   line=raw.strip()
   if not line or line.startswith("#") or line.startswith("//"): continue
   try:
    m=re.fullmatch(r'데이터베이스\s+"([^"]+)"',line)
    if m:
     if db: db.close()
     n=m.group(1); db=NexaDB(Path(filename).parent/(n if n.endswith(".db") else n+".db"))
     print("[NexaDB] 연결:",db.filename); continue
    if db is None: raise ValueError('먼저 데이터베이스 "이름"을 지정하세요.')
    m=re.fullmatch(r'테이블\s+([\w가-힣]+)\s+생성\s*\((.*)\)',line)
    if m:
     cols=[]
     for col in split_values(m.group(2)):
      bits=col.split()
      types={"문자":"TEXT","문자열":"TEXT","정수":"INTEGER","실수":"REAL","숫자":"REAL","참거짓":"INTEGER"}
      if len(bits)<2 or bits[1] not in types: raise ValueError("열 자료형을 확인하세요.")
      cols.append('"'+bits[0]+'" '+types[bits[1]])
     db.execute('CREATE TABLE IF NOT EXISTS "'+m.group(1)+'" ('+", ".join(cols)+")")
     print("[NexaDB] 테이블 준비:",m.group(1)); continue
    m=re.fullmatch(r'추가\s+([\w가-힣]+)\s*\((.*)\)',line)
    if m:
     vals=split_values(m.group(2))
     def val(v):
      v=v.strip()
      if len(v)>=2 and v[0] in "'\"" and v[-1]==v[0]: return v[1:-1]
      if v=="없음": return None
      if re.fullmatch(r"-?\d+",v): return int(v)
      if re.fullmatch(r"-?\d+\.\d+",v): return float(v)
      return v
     db.execute('INSERT INTO "'+m.group(1)+'" VALUES ('+",".join("?" for _ in vals)+")",[val(x) for x in vals])
     print("[NexaDB] 추가 완료"); continue
    m=re.fullmatch(r'조회\s+([\w가-힣]+)',line)
    if m: print(json.dumps(db.query('SELECT * FROM "'+m.group(1)+'"'),ensure_ascii=False,indent=2)); continue
    if line=="테이블목록": print(db.tables()); continue
    if line=="저장": db.commit(); print("[NexaDB] 저장 완료"); continue
    if line=="롤백": db.rollback(); print("[NexaDB] 롤백 완료"); continue
    m=re.fullmatch(r'실행\s+"(.*)"',line)
    if m:
     cur=db.execute(m.group(1))
     if cur.description: print(json.dumps([dict(x) for x in cur.fetchall()],ensure_ascii=False,indent=2))
     continue
    raise ValueError("알 수 없는 명령")
   except Exception as e: raise RuntimeError(f"{no}행: {e}") from e
 finally:
  if db: db.close()
