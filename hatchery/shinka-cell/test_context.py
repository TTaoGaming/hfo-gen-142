import unittest
from context import cleave

class ContextTests(unittest.TestCase):
    def test_native_format_variants_keep_identical_prefix_without_losing_instructions(self):
        outputs=[]
        for suffix in ('\nRewrite format A','\nRewrite format B'):
            original={'model':'packing-cell','messages':[{'role':'system','content':'Fixed policy'+suffix},{'role':'user','content':'Generation feedback'}]}
            result=cleave(original,'Fixed policy');outputs.append(result)
            self.assertEqual(''.join(m['content'] for m in result['messages'] if m['role']=='system'),original['messages'][0]['content'])
            self.assertEqual(result['messages'][-1],original['messages'][-1])
        self.assertEqual(outputs[0]['messages'][0],outputs[1]['messages'][0])
        self.assertNotEqual(outputs[0]['messages'][1],outputs[1]['messages'][1])

    def test_wrong_or_missing_policy_is_refused(self):
        for messages,prefix in [([],''),([{'role':'system','content':'changed'}],'Fixed policy'),([{'role':'user','content':'Fixed policy'}],'Fixed policy')]:
            with self.assertRaises(ValueError):cleave({'messages':messages},prefix)

if __name__=='__main__':unittest.main()
