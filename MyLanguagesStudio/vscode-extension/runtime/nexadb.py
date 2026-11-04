"""NexaDB SQLite runtime."""
import sqlite3
class NexaDB:
 def __init__(self,filename):
  self.conn=sqlite3.connect(filename); self.conn.row_factory=sqlite3.Row; self.conn.execute("PRAGMA foreign_keys=ON")
 def close(self): self.conn.close()
 def execute(self,sql,params=()):
  cur=self.conn.execute(sql,params); self.conn.commit(); return cur
 def query(self,sql,params=()): return [dict(r) for r in self.conn.execute(sql,params).fetchall()]
 def tables(self): return [r["name"] for r in self.query("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
