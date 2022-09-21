import json
from os.path import dirname
from os.path import join
from unittest import TestCase

from pytezos.michelson.forge import forge_micheline
from pytezos.michelson.forge import unforge_micheline
from pytezos.michelson.format import micheline_to_michelson
from pytezos.michelson.micheline import get_script_section
from pytezos.michelson.parse import michelson_to_micheline
from pytezos.michelson.program import MichelsonProgram
from pytezos.michelson.types.base import MichelsonType

folder = 'typed_minter'


class MainnetContractTestCaseTYPED_MARKETPLACE(TestCase):
    @classmethod
    def setUpClass(cls):
        with open(join(dirname(__file__), f'', '__script__.json')) as f:
            script = json.loads(f.read())

        cls.program = MichelsonProgram.match(script['code'])
        cls.script = script

        with open(join(dirname(__file__), f'', '__entrypoints__.json')) as f:
            entrypoints = json.loads(f.read())

        cls.entrypoints = entrypoints
        # cls.maxDiff = None

    def test_parameter_type_typed_marketplace(self):
        type_expr = self.program.parameter.as_micheline_expr()
        self.assertEqual(get_script_section(self.script, name='parameter'), type_expr, 'micheline -> type -> micheline')

    def test_entrypoints_typed_marketplace(self):
        ep_types = self.program.parameter.list_entrypoints()
        self.assertEqual(len(self.entrypoints['entrypoints']) + 1, len(ep_types))
        for name, ep_type in ep_types.items():
            if name not in ['default', 'root']:
                expected_type = MichelsonType.match(self.entrypoints['entrypoints'][name])
                expected_type.assert_type_equal(ep_type)

    def test_storage_type_typed_marketplace(self):
        type_expr = self.program.storage.as_micheline_expr()
        self.assertEqual(get_script_section(self.script, name='storage'), type_expr, 'micheline -> type -> micheline')

    def test_storage_encoding_typed_marketplace(self):
        val = self.program.storage.from_micheline_value(self.script['storage'])
        val_expr = val.to_micheline_value(mode='optimized')
        self.assertEqual(self.script['storage'], val_expr, 'micheline -> value -> micheline')

        val_ = self.program.storage.from_python_object(val.to_python_object())
        val_expr_ = val_.to_micheline_value(mode='optimized')
        self.assertEqual(self.script['storage'], val_expr_, 'value -> pyobj -> value -> micheline')

    def test_script_parsing_formatting(self):
        actual = michelson_to_micheline(micheline_to_michelson(self.script['code']))
        self.assertEqual(self.script['code'], actual)

    def test_storage_forging(self):
        expected = self.script['storage']
        actual = unforge_micheline(forge_micheline(expected))
        self.assertEqual(expected, actual)

        expected = self.program.storage.from_micheline_value(expected).to_micheline_value(mode='readable')
        actual = unforge_micheline(forge_micheline(expected))
        self.assertEqual(expected, actual)
