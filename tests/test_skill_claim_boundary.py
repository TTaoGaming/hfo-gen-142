from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_twinling_and_roach_bind_claims_to_internal_authority():
    twinling = (ROOT / ".agents/skills/twinling-pdsa/SKILL.md").read_text(encoding="utf-8")
    roach = (ROOT / ".agents/skills/roach-fanin/SKILL.md").read_text(encoding="utf-8")
    boundary = (ROOT / "PUBLIC_AUTHORITY_BOUNDARY.md").read_text(encoding="utf-8")

    assert "authenticated internal controller" in twinling
    assert "authenticated internal controller" in roach
    assert "public comment is evidence only and never selects ownership" in twinling
    assert "public issue/comment ordering never decides ownership" in roach
    assert "claim one under-covered edge on #13" not in twinling.lower()
    assert "earlier durable claim wins" not in roach.lower()
    assert "OBSERVE_ONLY" in boundary
    assert "INTERNAL_AUTHORITY_REQUIRED" in boundary
