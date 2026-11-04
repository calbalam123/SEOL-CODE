"""NexaDB: Korean-first SQLite database engine."""
import sqlite3
import json
from pathlib import Path
import re

class NexaDB:
    def __init__(self, filename):
        self.filename = str(Path(filename).resolve())
        self.conn = sqlite3.connect(self.filename)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
    def close(self):
        self.conn.close()
    def execute(self, sql, params=()):
        cur = self.conn.execute(sql, params)
        self.conn.commit()
        return cur
    def query(self, sql, params=()):
        cur = self.conn.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]
    def begin(self):
        self.conn.execute("BEGIN")
    def commit(self):
        self.conn.commit()
    def rollback(self):
        self.conn.rollback()
    def tables(self):
        return [r["name"] for r in self.query("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    def backup(self, destination):
        dest = sqlite3.connect(str(destination))
        self.conn.backup(dest)
        dest.close()

def _split_csv(s):
    out=[]; cur=""; quote=None; depth=0
    for ch in s:
        if quote:
            cur += ch
            if ch == quote: quote=None
        elif ch in ("'", '"'):
            quote=ch; cur += ch
        elif ch in "({[": depth += 1; cur += ch
        elif ch in ")}]": depth -= 1; cur += ch
        elif ch == "," and depth == 0: out.append(cur.strip()); cur=""
        else: cur += ch
    if cur.strip(): out.append(cur.strip())
    return out

def run_script(filename):
    db=None
    try:
        for line_no, raw in enumerate(Path(filename).read_text(encoding="utf-8-sig").splitlines(),1):
            line=raw.strip()
            if not line or line.startswith("#") or line.startswith("//"): continue
            try:
                m=re.fullmatch(r'(?:데이터베이스|데이터베이스열기)\s+"([^"]+)"', line)
                if m:
                    if db: db.close()
                    name=m.group(1)
                    db=NexaDB(Path(filename).parent / (name if name.endswith(".db") else name+".db"))
                    print(f"[NexaDB] 연결: {db.filename}")
                    continue
                if db is None: raise ValueError('먼저 데이터베이스 "이름"을 지정하세요.')
                m=re.fullmatch(r'테이블\s+([A-Za-z_가-힣][\w가-힣]*)\s+생성\s*\((.*)\)', line)
                if m:
                    cols=[]
                    for item in _split_csv(m.group(2)):
                        bits=item.split()
                        if len(bits)<2: raise ValueError("열은 '이름 자료형' 형식이어야 합니다.")
                        name, typ=bits[0], bits[1].upper()
                        types={"문자":"TEXT","문자열":"TEXT","정수":"INTEGER","실수":"REAL","숫자":"REAL","참거짓":"INTEGER"}
                        if typ not in (*types, "INTEGER","REAL","TEXT","BLOB"): raise ValueError(f"지원하지 않는 자료형: {typ}")
                        cols.append(f'"{name}" {types.get(typ,typ)} {" ".join(bits[2:])}'.strip())
                    db.execute(f'CREATE TABLE IF NOT EXISTS "{m.group(1)}" ({", ".join(cols)})')
                    print(f"[NexaDB] 테이블 생성/확인: {m.group(1)}")
                    continue
                m=re.fullmatch(r'추가\s+([A-Za-z_가-힣][\w가-힣]*)\s*\((.*)\)', line)
                if m:
                    vals=_split_csv(m.group(2))
                    def val(v):
                        v=v.strip()
                        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")): return v[1:-1]
                        if v=="없음": return None
                        if re.fullmatch(r"-?\d+",v): return int(v)
                        if re.fullmatch(r"-?\d+\.\d+",v): return float(v)
                        return v
                    db.execute(f'INSERT INTO "{m.group(1)}" VALUES ({", ".join("?" for _ in vals)})',[val(v) for v in vals])
                    print("[NexaDB] 데이터 추가 완료")
                    continue
                m=re.fullmatch(r'조회\s+([A-Za-z_가-힣][\w가-힣]*)(?:\s+조건\s+(.+))?', line)
                if m:
                    sql=f'SELECT * FROM "{m.group(1)}"'+(" WHERE "+m.group(2) if m.group(2) else "")
                    print(json.dumps(db.query(sql),ensure_ascii=False,indent=2))
                    continue
                if line=="테이블목록":
                    print("[NexaDB] 테이블:",", ".join(db.tables()) or "(없음)"); continue
                if line=="저장": db.commit(); print("[NexaDB] 저장 완료"); continue
                if line=="롤백": db.rollback(); print("[NexaDB] 롤백 완료"); continue
                m=re.fullmatch(r'실행\s+"(.*)"',line)
                if m:
                    cur=db.execute(m.group(1))
                    if cur.description: print(json.dumps([dict(x) for x in cur.fetchall()],ensure_ascii=False,indent=2))
                    continue
                raise ValueError("알 수 없는 명령입니다.")
            except Exception as e:
                raise RuntimeError(f"{line_no}행: {e}") from e
    finally:
        if db: db.close()
