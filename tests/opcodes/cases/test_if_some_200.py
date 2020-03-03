from unittest import TestCase

from tests import abspath

from pytezos.repl.interpreter import Interpreter
from pytezos.michelson.converter import michelson_to_micheline
from pytezos.repl.parser import parse_expression


class OpcodeTestif_some_200(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.i = Interpreter(debug=True)
        
    def test_opcode_if_some_200(self):
        res = self.i.execute(f'INCLUDE "{abspath("opcodes/contracts/if_some.tz")}"')
        self.assertTrue(res['success'])
        
        res = self.i.execute('RUN None "?"')
        self.assertTrue(res['success'])
        
        expected_expr = michelson_to_micheline('""')
        expected_val = parse_expression(expected_expr, res['result'][1].type_expr)
        self.assertEqual(expected_val, res['result'][1]._val)