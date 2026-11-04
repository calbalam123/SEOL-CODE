import sys
from nexadb import run_script
if len(sys.argv)<2:
    print("사용법: python nexadb_cli.py 파일.nql")
    raise SystemExit(2)
run_script(sys.argv[1])
