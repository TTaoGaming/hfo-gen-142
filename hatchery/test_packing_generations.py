import unittest
from pathlib import Path
from packing_generations import verify


class GeometryFalsifiers(unittest.TestCase):
    def test_reference_and_hostile_candidates(self):
        data = (Path(__file__).parent/'packing-fixture'/'parent.pck').read_bytes()
        self.assertEqual(verify(data)['pair_checks'], 7021)
        lines = data.decode().splitlines()
        controls = [lines[:-1], ['0.4']+lines[1:],
                    lines[:3]+[lines[2]]+lines[4:],
                    lines[:2]+['0 0 0']+lines[3:]]
        for changed in controls:
            with self.subTest(control=changed[:2]):
                with self.assertRaises(ValueError):
                    verify(('\n'.join(changed)+'\n').encode())


if __name__ == '__main__':
    unittest.main()
