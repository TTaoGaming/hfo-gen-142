import unittest
from evaluate import genome

class RecipeBoundary(unittest.TestCase):
    def test_data_only(self):
        valid="{'method':'full','noise':0.001,'beta':10000,'target_gain':1e-6,'maxiter':200,'seed':119}"
        self.assertEqual(genome(valid)['method'],'full')
        for bad in ["__import__('os').system('id')",valid.replace("'noise':0.001","'noise':1"),valid.replace("'seed':119","'seed':True"),valid[:-1]+",'command':'anything'}"]:
            with self.subTest(input=bad):
                with self.assertRaises((ValueError,SyntaxError)):
                    genome(bad)

if __name__=='__main__':unittest.main()
