import unittest

from seol_bot import BotCompileError, compile_bot


class BotCompilerTests(unittest.TestCase):
    def test_compile_basic_commands(self):
        result = compile_bot(
            '명령어("!안녕", "안녕하세요!")\n'
            '명령어("!버전", "설이 0.1")'
        )
        self.assertIn('case "!안녕":', result)
        self.assertIn('replier.reply("안녕하세요!");', result)
        self.assertIn('case "!버전":', result)
        self.assertIn("function response(", result)

    def test_compile_korean_and_newline(self):
        result = compile_bot('명령어("!도움말", "첫째 줄\\n둘째 줄")')
        self.assertIn(r'첫째 줄\n둘째 줄', result)

    def test_duplicate_command_is_rejected(self):
        with self.assertRaises(BotCompileError):
            compile_bot(
                '명령어("!안녕", "하이")\n'
                '명령어("!안녕", "안녕")'
            )

    def test_non_string_response_is_rejected(self):
        with self.assertRaises(BotCompileError):
            compile_bot('명령어("!숫자", 123)')

    def test_empty_source_is_rejected(self):
        with self.assertRaises(BotCompileError):
            compile_bot("")


if __name__ == "__main__":
    unittest.main()
