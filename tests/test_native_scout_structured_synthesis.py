import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "cloudflare" / "gen142-native-scout-r0" / "src" / "index.ts"


class NativeScoutStructuredSynthesisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SOURCE.read_text(encoding="utf-8")
        marker = 'const synthesis = await generateText({'
        start = cls.text.rfind(marker)
        cls.reducer_block = cls.text[start:start + 2200]

    def test_reducer_uses_schema_bound_output(self):
        self.assertIn('jsonSchema<ReducerOutput>', self.text)
        self.assertIn('output: Output.object({ schema: REDUCER_OUTPUT_SCHEMA })', self.reducer_block)
        self.assertIn('maxItems: 3', self.text)

    def test_reducer_disables_reasoning_only_for_terminal_synthesis(self):
        self.assertIn('reasoning_effort: null', self.reducer_block)
        self.assertIn('enable_thinking: false', self.reducer_block)

    def test_host_owns_authoritative_envelope_fields(self):
        self.assertIn('observed_utc: new Date().toISOString()', self.reducer_block)
        self.assertIn('canonical_recovery: "github:TTaoGaming/hfo-gen-142#13"', self.reducer_block)
        self.assertIn('...synthesis.output', self.reducer_block)

    def test_blank_text_path_is_not_terminal_contract(self):
        self.assertNotIn('synthesis.text.trim()', self.reducer_block)
        self.assertNotIn('EMPTY_SYNTHESIS', self.reducer_block)


if __name__ == '__main__':
    unittest.main()
