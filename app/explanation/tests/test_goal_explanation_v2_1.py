# app/explanation/tests/test_goal_explanation_v2.py

import pytest

from app.explanation.goal_template import GoalExplanationTemplate
from app.explanation.spec_goal_v2 import (
    HEADER,
    SECTION_DISTRIBUTION_INTRO,
    SECTION_RECENT_MATCHES_HEADER,
    WORDING_OVER_LEAN,
    WORDING_UNDER_LEAN,
    WORDING_NO_CLEAR_LEAN,
    VOLATILITY_WARNING,
)
from app.explanation.types import ComparableEvidenceSummary


FIXTURE = {
    "home_team": "Brentford",
    "away_team": "Sunderland",
}


def _mk_decision(
    pred: str,
    conf: str,
    over=0.62,
    under=0.38,
    volatility=False,
):
    return {
        "prediction": pred,
        "confidence": conf,
        "rates": {"over": over, "under": under},
        "volatility_flag": volatility,
        "reliability_score": 0.9,
        "sample_size": 25,
    }


def _mk_matches():
    return [
        {
            "metadata": {
                "home_team": "Brentford",
                "away_team": "Burnley",
                "season": "2025/26",
                "date": "2025-12-14",
                "total_goals": 3,
            }
        },
        {
            "metadata": {
                "home_team": "Fulham",
                "away_team": "Sunderland",
                "season": "2025/26",
                "date": "2025-11-30",
                "total_goals": 4,
            }
        },
    ]


@pytest.fixture
def evidence_summary():
    matches = _mk_matches()
    return ComparableEvidenceSummary(
        display_matches=matches,
        total_matches=len(matches),
        season_count=len({m["metadata"]["season"] for m in matches}),
    )

def test_header_is_fixed(evidence_summary):
    tpl = GoalExplanationTemplate()

    text = tpl.generate(
        fixture=FIXTURE,
        decision=_mk_decision("over_2_5", "moderate"),
        evidence_summary=evidence_summary,
    )

    assert text.startswith(HEADER)

def test_fixture_names_present(evidence_summary):
    tpl = GoalExplanationTemplate()

    text = tpl.generate(
        fixture=FIXTURE,
        decision=_mk_decision("over_2_5", "moderate"),
        evidence_summary=evidence_summary,
    )

    assert "Brentford vs Sunderland" in text

def test_over_under_no_clear_wording(evidence_summary):
    tpl = GoalExplanationTemplate()

    t_over = tpl.generate(
        fixture=FIXTURE,
        decision=_mk_decision("over_2_5", "moderate"),
        evidence_summary=evidence_summary,
    )
    assert WORDING_OVER_LEAN in t_over

    t_under = tpl.generate(
        fixture=FIXTURE,
        decision=_mk_decision("under_2_5", "moderate", 0.38, 0.62),
        evidence_summary=evidence_summary,
    )
    assert WORDING_UNDER_LEAN in t_under

    t_none = tpl.generate(
        fixture=FIXTURE,
        decision=_mk_decision("no_clear_lean", "low", 0.5, 0.5),
        evidence_summary=evidence_summary,
    )
    assert WORDING_NO_CLEAR_LEAN in t_none

def test_distribution_section_present(evidence_summary):
    tpl = GoalExplanationTemplate()

    text = tpl.generate(
        fixture=FIXTURE,
        decision=_mk_decision("over_2_5", "moderate"),
        evidence_summary=evidence_summary,
    )

    assert "Across comparable" in text
    assert "Over 2.5 goals:" in text
    assert "Under 2.5 goals:" in text
    assert "sample size" not in text.lower()

def test_distribution_section_present(evidence_summary):
    tpl = GoalExplanationTemplate()

    text = tpl.generate(
        fixture=FIXTURE,
        decision=_mk_decision("over_2_5", "moderate"),
        evidence_summary=evidence_summary,
    )

    assert "Across comparable" in text
    assert "Over 2.5 goals:" in text
    assert "Under 2.5 goals:" in text
    assert "sample size" not in text.lower()

def test_volatility_warning_included(evidence_summary):
    tpl = GoalExplanationTemplate()

    text = tpl.generate(
        fixture=FIXTURE,
        decision=_mk_decision("over_2_5", "low", volatility=True),
        evidence_summary=evidence_summary,
    )

    assert VOLATILITY_WARNING in text
