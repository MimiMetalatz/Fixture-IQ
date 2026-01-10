# app/explanation/goal_template.py

from app.explanation.spec_goal_v2 import (
    HEADER,
    SECTION_DISTRIBUTION_INTRO,
    SECTION_RECENT_MATCHES_HEADER,
    WORDING_OVER_LEAN,
    WORDING_UNDER_LEAN,
    WORDING_NO_CLEAR_LEAN,
    VOLATILITY_WARNING,
    CONFIDENCE_LOW,
    CONFIDENCE_MODERATE,
)
from app.explanation.types import ComparableEvidenceSummary


class GoalExplanationTemplate:
    @staticmethod
    def _format_prediction(pred: str) -> str:
        return {
            "over_2_5": "Over 2.5 goals",
            "under_2_5": "Under 2.5 goals",
            "no_clear_lean": "No clear lean",
        }[pred]

    def _format_opening(self, fixture: dict, decision: dict) -> str:
        home = fixture["home_team"]
        away = fixture["away_team"]
        conf = decision["confidence"]
        pred = decision["prediction"]

        if pred == "no_clear_lean":
            return (
                f"Based on the pre-match context, the {home} vs {away} fixture "
                "does not present a clear lean toward either Over or Under 2.5 goals."
            )

        return (
            f"Based on the pre-match context, the {home} vs {away} fixture "
            f"shows a {conf} confidence lean toward {self._format_prediction(pred)}."
        )

    def _format_reasoning(self, decision: dict) -> str:
        pred = decision["prediction"]
        volatility = decision.get("volatility_flag", False)

        if pred == "over_2_5":
            text = WORDING_OVER_LEAN
        elif pred == "under_2_5":
            text = WORDING_UNDER_LEAN
        else:
            text = WORDING_NO_CLEAR_LEAN

        if volatility:
            text += " " + VOLATILITY_WARNING

        return text

    def _format_distribution(self, decision: dict, evidence: ComparableEvidenceSummary) -> str:
        rates = decision["rates"]

        header = SECTION_DISTRIBUTION_INTRO.format(
            total_matches=evidence.total_matches,
            season_count=evidence.season_count,
        )

        body = (
            f"Over 2.5 goals: {rates['over']:.0%} · "
            f"Under 2.5 goals: {rates['under']:.0%}"
        )

        return f"{header}\n{body}"

    def _format_confidence_note(self, decision: dict) -> str:
        conf = decision["confidence"]

        if conf == "low":
            return CONFIDENCE_LOW
        if conf == "moderate":
            return CONFIDENCE_MODERATE
        return ""

    def _format_recent_matches(self, evidence: ComparableEvidenceSummary) -> str:
        if not evidence.display_matches:
            return ""

        lines = ["\n" + SECTION_RECENT_MATCHES_HEADER]

        for m in evidence.display_matches:
            md = m["metadata"]
            lines.append(
                f"• {md['home_team']} vs {md['away_team']} "
                f"({md['season']}) – "
                f"{'Over 2.5 goals' if md['total_goals'] > 2.5 else 'Under 2.5 goals'}"
            )

        return "\n".join(lines)

    def generate(
        self,
        *,
        fixture: dict,
        decision: dict,
        evidence_summary: ComparableEvidenceSummary,
    ) -> str:
        parts = [
            HEADER,
            "",
            self._format_opening(fixture, decision),
            "",
            self._format_reasoning(decision),
            "",
            self._format_distribution(decision, evidence_summary),
            "",
            f"Prediction: {self._format_prediction(decision['prediction'])}",
            f"Confidence: {decision['confidence'].capitalize()}",
        ]

        confidence_note = self._format_confidence_note(decision)
        if confidence_note:
            parts.extend(["", confidence_note])

        recent = self._format_recent_matches(evidence_summary)
        if recent:
            parts.append(recent)

        return "\n".join(parts)
