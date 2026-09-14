"""Finite CPU-only two-generation assay over an existing spherical packing.

The native supervisor owns process limits. This program owns no scheduler,
provider credentials, remote submissions or retries. Retention is a valid outcome.
"""
import hashlib
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify(data):
    lines = data.decode('ascii').splitlines()
    radius = Fraction(lines[0])
    rows = [[Fraction(v) for v in line.split()] for line in lines[2:]]
    if not (0 < radius < 1 and len(rows) == 119 and all(len(row) == 6 for row in rows)):
        raise ValueError('invalid packing shape')
    walls = [(1-radius)**2-sum(v*v for v in row) for row in rows]
    pairs = [sum((a-b)**2 for a,b in zip(rows[i],rows[j]))-4*radius**2
             for i in range(119) for j in range(i)]
    if min(walls) < 0 or min(pairs) < 0:
        raise ValueError('infeasible packing')
    return {'radius': str(radius), 'containment_checks': len(walls),
            'pair_checks': len(pairs), 'min_wall_slack': str(min(walls)),
            'min_pair_slack': str(min(pairs))}


def run(root):
    root = Path(root).resolve()
    parent = (root/'parent.pck').read_bytes()
    kernel = (root/'refine.py').read_bytes()
    evaluator_sha = sha(Path(__file__).read_bytes())
    # Admission binds the scientific kernel and original input before execution.
    admission = json.loads((root/'admission.json').read_text())
    if admission != {'parent_sha256': sha(parent), 'kernel_sha256': sha(kernel),
                     'evaluator_sha256': evaluator_sha, 'generations': 2,
                     'provider_calls': 0, 'retries': 0}:
        raise ValueError('admission mismatch')
    verify(parent)
    receipts = []
    for generation in (1, 2):
        folder = root/f'generation-{generation}'
        folder.mkdir(exist_ok=False)
        (folder/'parent.pck').write_bytes(parent)
        (folder/'refine.py').write_bytes(kernel)
        result = subprocess.run([sys.executable, 'refine.py', str(generation)],
                                cwd=folder, capture_output=True, timeout=100)
        if result.returncode:
            raise RuntimeError(f'kernel failed: generation {generation}, exit {result.returncode}')
        candidate = (folder/'best.pck').read_bytes() if (folder/'best.pck').exists() else parent
        evidence = verify(candidate)
        improved = Fraction(evidence['radius']) > Fraction(verify(parent)['radius'])
        accepted = candidate if improved else parent
        (folder/'accepted.pck').write_bytes(accepted)
        receipt = {'generation': generation, 'parent_sha256': sha(parent),
                   'accepted_sha256': sha(accepted), 'kernel_sha256': sha(kernel),
                   'evaluator_sha256': evaluator_sha, 'verdict': 'IMPROVED' if improved else 'RETAINED',
                   'verification': verify(accepted), 'provider_calls': 0, 'retries': 0,
                   'search': json.loads((folder/'search.json').read_text())}
        (folder/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
        receipts.append(receipt)
        parent = accepted
    assert receipts[1]['parent_sha256'] == receipts[0]['accepted_sha256']
    summary = {'status': 'TWO_VERIFIED_GENERATIONS', 'generations': receipts,
               'scope': 'Finite CPU refinement; not LLM-driven MOME or unattended orchestration.'}
    (root/'result.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary))


if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv)>1 else '.')
