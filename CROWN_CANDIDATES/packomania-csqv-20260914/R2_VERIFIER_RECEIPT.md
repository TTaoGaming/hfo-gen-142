# Packomania R2 exact-bytes verifier receipt

- packaging carrier UUID: `6c4fa680-c4e8-45e9-bce2-223f619c1b36`
- packet branch: `twinling/packomania-packet-r2-6c4fa680`
- independent verifier implementation: `jasonzliang/circle-packing-sota@28e129593b1c696627db67911b0392c439c64610`
- verifier program: `verify_and_compare.py`
- verifier property: public pure-stdlib implementation, separate from the Discovery Loop producer solver
- tolerance: `0`
- external submission performed: `false`
- crown/keeper acceptance: `PENDING`

## Exact attachment bytes

| N | SHA-256 | current keeper record | result |
|---:|---|---:|---|
| 120 | `5921e2ca32b2da8c8f908caaeaa9decc6498fd51b5e98006c96b1fe0571fa63a` | `5.773179664812` | `STRICTLY FEASIBLE`; beats record |
| 122 | `87af14334f54bb1c517e8e5d5cd36c38302f5b34bc0eca9a851641e59e73247f` | `5.822533741922` | `STRICTLY FEASIBLE`; beats record |

Verifier readback also parsed `author: Tommy Tai`, `N=120/122`, positive radius minima, minimum wall slack about `1e-10`, and minimum pair slack about `2e-10` for both files.

## Command shape

```text
python3 verify_and_compare.py verify csqv120.pck --record 5.773179664812 --tol 0
python3 verify_and_compare.py verify csqv122.pck --record 5.822533741922 --tol 0
```

Both commands returned `STRICTLY FEASIBLE (tol 0): True` and `BEATS the record` against the recorded keeper values.

## Boundary

This is exact-byte mathematical verification, not third-party keeper acceptance and not a self-awarded crown. Re-fetch the official keeper immediately before human send. Reusable skill/heritage admission from this packaging cycle is `NONE`; any reusable gene still requires verifier + downstream ConsumerAck.
