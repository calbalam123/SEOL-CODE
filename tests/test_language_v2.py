import contextlib
import io
import unittest
from seol_language import Interpreter, SeolError

class ExpandedLanguageTests(unittest.TestCase):
    def run_code(self, source):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            Interpreter().run(source)
        return stream.getvalue().strip()

    def test_function_return(self):
        self.assertEqual(self.run_code('함수 더하기(a, b):\n    반환 a + b\n출력(더하기(2, 3))'), '5')

    def test_list_loop(self):
        self.assertEqual(self.run_code('과일 = ["사과", "배"]\n반복 항목 in 과일:\n    출력(항목)'), '사과\n배')

    def test_list_and_helpers(self):
        self.assertEqual(self.run_code('숫자 = [2, 3]\n추가(숫자, 5)\n출력(숫자[2], 합계(숫자))'), '5 10')

    def test_dictionary(self):
        self.assertEqual(self.run_code('정보 = {"이름": "설이"}\n만약 "이름" in 정보:\n    출력(정보["이름"])'), '설이')

    def test_missing_variable(self):
        with self.assertRaisesRegex(SeolError, '변수를 찾을 수 없습니다'):
            Interpreter().run('출력(없는값)')

if __name__ == '__main__':
    unittest.main()
