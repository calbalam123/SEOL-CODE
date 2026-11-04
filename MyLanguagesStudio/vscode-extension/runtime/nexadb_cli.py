import sys
from nexadb import run_script
if len(sys.argv)<2: raise SystemExit("사용법: nexadb_cli.py 파일.nql")
run_script(sys.argv[1])
