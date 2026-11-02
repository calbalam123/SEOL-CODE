import contextlib
import io
import unittest
from seol_language import Interpreter

class BuiltinLibraryTests(unittest.TestCase):
    def run_code(self, source):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            Interpreter().run(source)
        return stream.getvalue().strip()

    def test_exactly_100_registered_functions(self):
        from seol_builtins import BUILTINS
        self.assertEqual(len(BUILTINS), 100)

    def test_math_functions(self):
        self.assertEqual(self.run_code('출력(제곱근(81), 평균([2, 4, 6]), 백분율(1, 4))'), '9.0 4 25.0')

    def test_string_functions(self):
        self.assertEqual(self.run_code('출력(대문자(공백제거(" hi ")), 문자개수("banana", "a"))'), 'HI 3')

    def test_list_and_dictionary_functions(self):
        self.assertEqual(self.run_code('가 = [1, 2]\n목록추가(가, 3)\n출력(마지막항목(가), 사전가져오기({"x": 7}, "x"))'), '3 7')

    def test_json_and_date_functions(self):
        self.assertEqual(self.run_code('출력(JSON읽기(JSON문자열({"ok": 참}))["ok"])'), 'True')

if __name__ == "__main__":
    unittest.main()
