import re
from app.explanation.outcome_template import OutcomeExplanationTemplate
from app.explanation.spec_outcome_v1 import (
    HEADER,
    SECTION_DISTRIBUTION_INTRO,
    SECTION_RECENT_MATCHES_HEADER,
    OutcomePrediction,
    ConfidenceLevel,
    WORDING_NO_CLEAR_LEAN,
    WORDING_LOW_LEAN,
    WORDING_MODERATE_LEAN,
    WORDING_HIGH_LEAN,
)


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


def test_header_is_fixed():
    tpl = OutcomeExplanationTemplate()
    text = tpl.generate({}, _mk_decision("home", "moderate"))
    assert text.startswith(HEADER)


def test_distribution_format_present_and_no_sample_size_jargon():
    tpl = OutcomeExplanationTemplate()
    text = tpl.generate({}, _mk_decision("home", "moderate"))

    assert SECTION_DISTRIBUTION_INTRO in text
    assert "Home wins:" in text and "Draws:" in text and "Away wins:" in text

    # Must not show jargon
    assert "sample size" not in text.lower()


def test_confidence_wording_variants():
    tpl = OutcomeExplanationTemplate()

    # No clear lean
    t0 = tpl.generate({}, _mk_decision("no_clear_lean", "low", 0.32, 0.32, 0.36))
    assert WORDING_NO_CLEAR_LEAN in t0

    # Low lean
    t1 = tpl.generate({}, _mk_decision("away", "low"))
    assert WORDING_LOW_LEAN.format(side="the away side") in t1

    # Moderate lean
    t2 = tpl.generate({}, _mk_decision("home", "moderate"))
    assert WORDING_MODERATE_LEAN.format(side="the home side") in t2

    # High lean
    t3 = tpl.generate({}, _mk_decision("draw", "high"))
    assert WORDING_HIGH_LEAN.format(side="a draw") in t3


def test_recent_matches_section_optional_and_formatted():
    tpl = OutcomeExplanationTemplate()
    matches = _mk_matches()
    text = tpl.generate({}, _mk_decision("home", "moderate"), display_matches=matches)

    assert SECTION_RECENT_MATCHES_HEADER in text

    # Outcome code translated
    assert "– Home win" in text
    assert "– Draw" in text

    # Season formatted '2025/26' style (from both '2025/2026' and '2526')
    assert "(2025/26)" in text


def test_recent_matches_section_absent_when_none():
    tpl = OutcomeExplanationTemplate()
    text = tpl.generate({}, _mk_decision("home", "moderate"), display_matches=None)
    assert SECTION_RECENT_MATCHES_HEADER not in text
