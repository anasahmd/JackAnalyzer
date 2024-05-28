import unittest
from JackAnalyzer import JackTokenizer

class TestJackAnalyzer(unittest.TestCase):
    def setUp(self):
        self.tokenizer = JackTokenizer()

    def test_remove_inline_comment(self):
        input_string = "let x = 5;// This is an inline comment"
        expected_output = "let x = 5;"
        self.assertEqual(self.tokenizer.remove_inline_comment(input_string), expected_output)
        
    def test_remove_inline_comment_no_comments(self):
        input_string = "let x = 5;"
        expected_output = "let x = 5;"
        self.assertEqual(self.tokenizer.remove_inline_comment(input_string), expected_output)

    def test_remove_multiline_comment_start(self):
        input_string = "let x = 5;/* This is a multi-line comment"
        expected_output = "let x = 5;"
        self.assertEqual(self.tokenizer.remove_multi_line_comment(input_string), expected_output)
        self.assertTrue(self.tokenizer.multi_comment)

    def test_remove_multiline_comment_end(self):
        input_string = " This is still a multi-line comment */let y = 10;"
        self.tokenizer.multi_comment = True
        expected_output = "let y = 10;"
        self.assertEqual(self.tokenizer.remove_multi_line_comment(input_string), expected_output)
        self.assertFalse(self.tokenizer.multi_comment)

    def test_remove_comments(self):
        input_string = "let z = 15;"
        expected_output = "let z = 15;"
        self.assertEqual(self.tokenizer.remove_comments(input_string), expected_output)
        self.assertFalse(self.tokenizer.multi_comment)

    def test_multiline_comment_within_line(self):
        input_string = "let x = 5;/* comment */let y = 10;"
        expected_output = "let x = 5;let y = 10;"
        self.assertEqual(self.tokenizer.remove_comments(input_string), expected_output)
        
    def test_advance(self):
        self.tokenizer.add_new_line('let x = 5;')
        self.tokenizer.advance()
        self.assertEqual(self.tokenizer.tokenType(), 'KEYWORD')
        self.assertEqual(self.tokenizer.keyWord(), 'LET')
        self.tokenizer.advance()
        self.assertEqual(self.tokenizer.tokenType(), 'IDENTIFIER')
        self.assertEqual(self.tokenizer.identifier(), 'x')
        self.tokenizer.advance()
        self.assertEqual(self.tokenizer.tokenType(), 'SYMBOL')
        self.assertEqual(self.tokenizer.identifier(), '=')
        self.tokenizer.advance()
        self.assertEqual(self.tokenizer.tokenType(), 'INT_CONST')
        self.assertEqual(self.tokenizer.intVal(), 5)

if __name__ == '__main__':
    unittest.main()