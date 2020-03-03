from unittest import TestCase

from tests import abspath

from pytezos.repl.interpreter import Interpreter
from pytezos.michelson.converter import michelson_to_micheline
from pytezos.repl.parser import parse_expression


class OpcodeTestconcat_hello_168(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.i = Interpreter(debug=True)
        
    def test_opcode_concat_hello_168(self):
        res = self.i.execute(f'INCLUDE "{abspath("opcodes/contracts/concat_hello.tz")}"')
        self.assertTrue(res['success'])
        
        res = self.i.execute('RUN { "test1" ; "test2" } {}')
        self.assertTrue(res['success'])
        
        expected_expr = michelson_to_micheline('{ "Hello test1" ; "Hello test2" }')
        expected_val = parse_expression(expected_expr, res['result'][1].type_expr)
        self.assertEqual(expected_val, res['result'][1]._val)