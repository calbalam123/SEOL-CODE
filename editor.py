#!/usr/bin/env python3
"""설이코드 전용 Windows 편집기. 표준 Tkinter만 사용합니다."""
from __future__ import annotations
import contextlib
import io
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from seol_language import Interpreter, SeolError, VERSION

class SeolEditor:
    def __init__(self, root):
        self.root = root
        self.path = None
        self.root.title(f"설이코드 편집기 - SEOL CODE {VERSION}")
        self.root.geometry("1050x720")
        self.root.minsize(760, 520)
        self._style()
        self._menu()
        self._toolbar()

        self.panes = ttk.Panedwindow(root, orient=tk.VERTICAL)
        self.panes.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        code_frame = ttk.Frame(self.panes)
        output_frame = ttk.Frame(self.panes)
        self.panes.add(code_frame, weight=4)
        self.panes.add(output_frame, weight=1)

        ttk.Label(code_frame, text="코드 편집").pack(anchor="w", pady=(4, 5))
        editor_wrap = ttk.Frame(code_frame)
        editor_wrap.pack(fill=tk.BOTH, expand=True)
        self.code = tk.Text(editor_wrap, wrap="none", undo=True, font=("Malgun Gothic", 12),
                            bg="#171923", fg="#f1f2f6", insertbackground="white",
                            selectbackground="#394867", padx=12, pady=10)
        ybar = ttk.Scrollbar(editor_wrap, orient="vertical", command=self.code.yview)
        xbar = ttk.Scrollbar(editor_wrap, orient="horizontal", command=self.code.xview)
        self.code.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        self.code.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        editor_wrap.rowconfigure(0, weight=1)
        editor_wrap.columnconfigure(0, weight=1)

        ttk.Label(output_frame, text="실행 결과").pack(anchor="w", pady=(8, 5))
        self.output = tk.Text(output_frame, height=9, wrap="word", state="disabled",
                              font=("Malgun Gothic", 10), bg="#10131a", fg="#d9e2f2",
                              padx=10, pady=8)
        self.output.pack(fill=tk.BOTH, expand=True)
        self.status = tk.StringVar(value="새 파일")
        ttk.Label(root, textvariable=self.status, anchor="w").pack(fill="x", padx=10, pady=(0, 6))
        self.code.insert("1.0", '# 설이코드 첫 프로그램\n출력("안녕하세요! 설이코드입니다.")\n')
        self.code.bind("<Control-s>", lambda e: self.save())
        self.code.bind("<Control-o>", lambda e: self.open_file())
        self.code.bind("<F5>", lambda e: self.run_code())
        self.code.bind("<Control-n>", lambda e: self.new_file())
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def _style(self):
        style = ttk.Style()
        try: style.theme_use("clam")
        except tk.TclError: pass
        style.configure("TButton", font=("Malgun Gothic", 10), padding=7)
        style.configure("TLabel", font=("Malgun Gothic", 10))
        style.configure("TMenubutton", font=("Malgun Gothic", 10))

    def _menu(self):
        bar = tk.Menu(self.root)
        file_menu = tk.Menu(bar, tearoff=False)
        file_menu.add_command(label="새 파일", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="열기", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="저장", accelerator="Ctrl+S", command=self.save)
        file_menu.add_command(label="다른 이름으로 저장", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.close)
        bar.add_cascade(label="파일", menu=file_menu)
        run_menu = tk.Menu(bar, tearoff=False)
        run_menu.add_command(label="실행", accelerator="F5", command=self.run_code)
        run_menu.add_command(label="출력 지우기", command=self.clear_output)
        bar.add_cascade(label="실행", menu=run_menu)
        help_menu = tk.Menu(bar, tearoff=False)
        help_menu.add_command(label="설이코드 문법 도움말", command=self.help)
        help_menu.add_command(label="버전 정보", command=lambda: messagebox.showinfo("설이코드", f"SEOL CODE {VERSION}"))
        bar.add_cascade(label="도움말", menu=help_menu)
        self.root.config(menu=bar)

    def _toolbar(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill="x", padx=8, pady=8)
        ttk.Button(frame, text="새 파일", command=self.new_file).pack(side="left", padx=3)
        ttk.Button(frame, text="열기", command=self.open_file).pack(side="left", padx=3)
        ttk.Button(frame, text="저장", command=self.save).pack(side="left", padx=3)
        ttk.Button(frame, text="▶ 실행 (F5)", command=self.run_code).pack(side="left", padx=12)
        ttk.Button(frame, text="출력 지우기", command=self.clear_output).pack(side="left", padx=3)

    def _write_output(self, text):
        self.output.configure(state="normal")
        self.output.insert("end", text)
        self.output.see("end")
        self.output.configure(state="disabled")

    def clear_output(self):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")

    def run_code(self):
        source = self.code.get("1.0", "end-1c")
        self.clear_output()
        stream = io.StringIO()
        try:
            with contextlib.redirect_stdout(stream):
                Interpreter().run(source, str(self.path or "<편집기>"))
            result = stream.getvalue()
            self._write_output(result if result else "실행 완료 (출력 없음)\n")
            self.status.set("실행 완료")
        except SeolError as exc:
            self._write_output(f"설이코드 오류: {exc}\n")
            self.status.set("오류 발생")
        except Exception as exc:
            self._write_output(f"오류: {exc}\n")
            self.status.set("오류 발생")

    def new_file(self):
        if not self._confirm_discard(): return
        self.path = None
        self.code.delete("1.0", "end")
        self.status.set("새 파일")

    def open_file(self):
        if not self._confirm_discard(): return
        name = filedialog.askopenfilename(filetypes=[("설이코드 파일", "*.seol"), ("모든 파일", "*.*")])
        if not name: return
        try:
            self.code.delete("1.0", "end")
            self.code.insert("1.0", Path(name).read_text(encoding="utf-8"))
            self.path = Path(name)
            self.status.set(str(self.path))
        except OSError as exc:
            messagebox.showerror("열기 실패", str(exc))

    def save(self):
        if self.path is None: return self.save_as()
        try:
            self.path.write_text(self.code.get("1.0", "end-1c"), encoding="utf-8")
            self.status.set(f"저장됨: {self.path}")
            return True
        except OSError as exc:
            messagebox.showerror("저장 실패", str(exc))
            return False

    def save_as(self):
        name = filedialog.asksaveasfilename(defaultextension=".seol",
            filetypes=[("설이코드 파일", "*.seol"), ("텍스트 파일", "*.txt")])
        if not name: return False
        self.path = Path(name)
        return self.save()

    def _confirm_discard(self):
        if not self.code.get("1.0", "end-1c").strip(): return True
        return messagebox.askyesno("확인", "현재 코드를 저장했나요? 계속 진행할까요?")

    def help(self):
        messagebox.showinfo("설이코드 기본 문법",
            '출력("안녕")\n이름 = "설이"\n만약 점수 >= 60:\n    출력("합격")\n아니면:\n    출력("불합격")\n반복 3회:\n    출력("반복")\n반복 항목 in ["사과", "배"]:\n    출력(항목)\n함수 더하기(a, b):\n    반환 a + b\n출력(더하기(2, 3))\n\n내장 함수: 길이, 문자열, 정수, 실수, 반올림, 절댓값, 최댓값, 최솟값, 합계, 추가, 포함')

    def close(self):
        self.root.destroy()

def main():
    root = tk.Tk()
    SeolEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
