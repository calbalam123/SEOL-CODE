import contextlib
import io
import unittest

from seol import Interpreter, SeolError


class InterpreterTests(unittest.TestCase):
    def run_code(self, source):
        output = io.StringIO()
        interpreter = Interpreter()
        with contextlib.redirect_stdout(output):
            interpreter.run(source)
        return output.getvalue().strip()

    def test_print_and_variable(self):
        self.assertEqual(
            self.run_code('이름 = "설이"\n출력("안녕 " + 이름)'),
            "안녕 설이",
        )

    def test_if_else(self):
        result = self.run_code(
            "점수 = 90\n"
            "만약 점수 >= 60:\n"
            '    출력("합격")\n'
            "아니면:\n"
            '    출력("불합격")'
        )
        self.assertEqual(result, "합격")

    def test_repeat(self):
        result = self.run_code('반복 3회:\n    출력("반복")')
        self.assertEqual(result.splitlines(), ["반복", "반복", "반복"])

    def test_function(self):
        result = self.run_code(
            "함수 인사(이름):\n"
            '    출력("안녕 " + 이름)\n'
            '인사("설이")'
        )
        self.assertEqual(result, "안녕 설이")

    def test_unknown_variable_has_korean_error(self):
        with self.assertRaisesRegex(SeolError, "변수를 찾을 수 없습니다"):
            Interpreter().run("출력(없는변수)")


if __name__ == "__main__":
    unittest.main()
