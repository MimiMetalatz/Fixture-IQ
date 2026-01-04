import pytest

from app.explanation.outcome_template import OutcomeExplanationTemplate
from app.explanation.spec_outcome_v1 import (
    HEADER,
    SECTION_DISTRIBUTION_INTRO,
    SECTION_RECENT_MATCHES_HEADER,
    WORDING_NO_CLEAR_LEAN,
    WORDING_LOW_LEAN,
    WORDING_MODERATE_LEAN,
    WORDING_HIGH_LEAN,
)
from app.explanation.types import ComparableEvidenceSummary

fixture={"home_team": "Leeds", "away_team": "Man United"}

def fixture_label(fixture: dict) -> str:
    return f"{fixture['home_team']} vs {fixture['away_team']}"

def _mk_decision(pred: str, conf: str, h=0.48, d=0.16, a=0.36):
    return {
        "prediction": pred,
        "confidence": conf,
        "rates": {"H": h, "D": d, "A": a},
        "sample_size": 25,  # allowed to exist internally, but must NOT be displayed
    }

def _mk_matches():
    return [
        {
            "metadata": {
                "home_team": "Arsenal",
                "away_team": "Aston Villa",
                "season": "2025/2026",
                "date": "2026-01-01",
                "outcome": "H",
            }
        },
        {
            "metadata": {
                "home_team": "Tottenham",
                "away_team": "Man United",
                "season": "2526",
                "date": "2025-12-20",
                "outcome": "D",
            }
        },
    ]

@pytest.fixture
def comparable_matches():
    return _mk_matches()

@pytest.fixture
def evidence_summary() -> ComparableEvidenceSummary:
    matches = _mk_matches()
    return ComparableEvidenceSummary(
        display_matches=matches,
        total_matches=len(matches),
        season_count=len({m["metadata"].get("season") for m in matches}),
    )

def test_header_is_fixed(evidence_summary):
    tpl = OutcomeExplanationTemplate()

    text = tpl.generate(
        decision=_mk_decision("home", "moderate"),
        fixture=fixture,
        evidence_summary=evidence_summary,
    )

    assert text.startswith(HEADER)

def test_distribution_format_present_and_no_sample_size_jargon(evidence_summary):
    tpl = OutcomeExplanationTemplate()
    text = tpl.generate(decision=_mk_decision("home", "moderate"), fixture=fixture, evidence_summary=evidence_summary)

    assert "Home wins:" in text 
    assert "Draws:" in text 
    assert "Away wins:" in text
    # Must not show jargon
    assert "sample size" not in text.lower()

def test_confidence_wording_variants(evidence_summary):
    tpl = OutcomeExplanationTemplate()

    # No clear lean
    t0 = tpl.generate(decision=_mk_decision("no_clear_lean", "low", 0.32, 0.32, 0.36), fixture=fixture, evidence_summary=evidence_summary)
    assert WORDING_NO_CLEAR_LEAN.format(fixture=fixture_label(fixture)) in t0

    # Low lean
    t1 = tpl.generate(decision=_mk_decision("away", "low"), fixture=fixture, evidence_summary=evidence_summary)
    assert WORDING_LOW_LEAN.format(fixture=fixture_label(fixture), side="the away side") in t1

    # Moderate lean
    t2 = tpl.generate(decision=_mk_decision("home", "moderate"), fixture=fixture, evidence_summary=evidence_summary)
    assert WORDING_MODERATE_LEAN.format(fixture=fixture_label(fixture), side="the home side") in t2

    # High lean
    t3 = tpl.generate(decision=_mk_decision("draw", "high"), fixture=fixture, evidence_summary=evidence_summary)
    assert WORDING_HIGH_LEAN.format(fixture=fixture_label(fixture), side="a draw") in t3
    
def test_no_clear_lean_wording(evidence_summary):
    tpl = OutcomeExplanationTemplate()

    text = tpl.generate(
        decision=_mk_decision("no_clear_lean", "low", 0.32, 0.32, 0.36),
        fixture=fixture,
        evidence_summary=evidence_summary,
    )

    expected = (
        f"Based on the pre-match context, the {fixture_label(fixture)} fixture "
        "does not present a clear outcome lean."
    )

    assert expected in text

def test_low_confidence_wording(evidence_summary):
    tpl = OutcomeExplanationTemplate()

    text = tpl.generate(
        decision=_mk_decision("away", "low"),
        fixture=fixture,
        evidence_summary=evidence_summary,
    )

    expected = (
        f"Based on the pre-match context, the {fixture_label(fixture)} fixture "
        "shows a slight lean toward the away side."
    )

    assert expected in text

def test_moderate_confidence_wording(evidence_summary):
    tpl = OutcomeExplanationTemplate()

    text = tpl.generate(
        decision=_mk_decision("home", "moderate"),
        fixture=fixture,
        evidence_summary=evidence_summary,
    )

    expected = (
        f"Based on the pre-match context, the {fixture_label(fixture)} fixture "
        "shows a moderate confidence lean toward the home side."
    )

    assert expected in text

def test_high_confidence_wording(evidence_summary):
    tpl = OutcomeExplanationTemplate()

    text = tpl.generate(
        decision=_mk_decision("draw", "high"),
        fixture=fixture,
        evidence_summary=evidence_summary,
    )

    expected = (
        f"Based on the pre-match context, the {fixture_label(fixture)} fixture "
        "shows a high confidence lean toward a draw."
    )

    assert expected in text

def test_recent_matches_section_optional_and_formatted(evidence_summary):
    tpl = OutcomeExplanationTemplate()

    text = tpl.generate(decision=_mk_decision("home", "moderate"), fixture=fixture, evidence_summary=evidence_summary)

    assert SECTION_RECENT_MATCHES_HEADER in text

    # Outcome code translated
    assert "– Home win" in text
    assert "– Draw" in text

    # Season formatted '2025/26' style (from both '2025/2026' and '2526')
    assert "(2025/26)" in text

def test_no_template_placeholders_leak(evidence_summary):
    tpl = OutcomeExplanationTemplate()

    text = tpl.generate(
        decision=_mk_decision("home", "moderate"),
        fixture=fixture,
        evidence_summary=evidence_summary,
    )

    assert "{fixture}" not in text
    assert "{side}" not in text


def test_recent_matches_section_absent_when_no_summary():
    tpl = OutcomeExplanationTemplate()
    text = tpl.generate(decision=_mk_decision("home", "moderate"), fixture=fixture, evidence_summary=None)
    assert SECTION_RECENT_MATCHES_HEADER not in text
