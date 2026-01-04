from pyparsing import Optional
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

from app.utils.logging import get_explanation_logger

logger = get_explanation_logger()

class OutcomeExplanationTemplate:
    # ---------- Helpers ----------
    @staticmethod
    def _format_season(season: str) -> str:
        if "/" in season:
            start, end = season.split("/")
            return f"{start}/{end[-2:]}"
        return f"20{season[:2]}/{season[2:]}"  # fallback

    @staticmethod
    def _format_outcome(outcome: str) -> str:
        return {
            "H": "Home win",
            "D": "Draw",
            "A": "Away win",
        }.get(outcome, outcome)

    def _format_comparable_matches(self, matches):
        if not matches:
            return ""

        lines = [SECTION_RECENT_MATCHES_HEADER]
        for m in matches:
            md = m["metadata"]
            lines.append(
                f"• {md['home_team']} vs {md['away_team']} "
                f"({self._format_season(md['season'])}) – "
                f"{self._format_outcome(md['outcome'])}"
            )

        return "\n".join(lines)

    # ---------- Confidence-aware assessment ----------
    def _assessment_text(self, pred: str, conf: str, fixture_label: str) -> str:
        if pred == "no_clear_lean":
            return WORDING_NO_CLEAR_LEAN.format(fixture=fixture_label)

        side = {
            "home": "the home side",
            "away": "the away side",
            "draw": "a draw",
        }[pred]

        if conf == "low":
            return WORDING_LOW_LEAN.format(fixture=fixture_label, side=side)
        if conf == "moderate":
            return WORDING_MODERATE_LEAN.format(fixture=fixture_label, side=side)
        if conf == "high":
            return WORDING_HIGH_LEAN.format(fixture=fixture_label,side=side)

        return WORDING_LOW_LEAN.format(fixture=fixture_label, side=side)

    # ---------- Main generator ----------    
    def generate(self, decision: dict, fixture: dict, evidence_summary: ComparableEvidenceSummary | None = None) -> str:
        pred = decision["prediction"]
        conf = decision["confidence"]
        rates = decision["rates"]
        if evidence_summary:
            display_matches = evidence_summary.display_matches
            total_matches = evidence_summary.total_matches
            season_count = evidence_summary.season_count
        else:
            display_matches = None
            total_matches = None
            season_count = None

        logger.info(
            "Outcome explanation generated | "
            f"schema=outcome_v1 | "
            f"prediction={pred} | "
            f"confidence={conf} | "
            f"rates={rates}"
        )

        fixture_label = f"{fixture['home_team']} vs {fixture['away_team']}"
        assessment = self._assessment_text(pred, conf, fixture_label=fixture_label)

        distribution = (
            f"{SECTION_DISTRIBUTION_INTRO.format(total_matches=total_matches, season_count=season_count)}\n"
            f"Home wins: {rates['H']:.0%} · "
            f"Draws: {rates['D']:.0%} · "
            f"Away wins: {rates['A']:.0%}"
        )

        prediction_text = (
            "Prediction: No clear lean"
            if pred == "no_clear_lean"            
            else f"Prediction: {pred.capitalize()}"
        )

        confidence_text = f"Confidence: {conf.capitalize()}"

        comparable_text = self._format_comparable_matches(display_matches)
        comparable_block = f"\n\n{comparable_text}" if comparable_text else ""

        if display_matches:
            seasons = sorted(
                {m["metadata"].get("season") for m in display_matches}
            )
            logger.info(
                "Comparable fixtures displayed | "
                f"count={len(display_matches)} | "
                f"seasons={seasons}"
            )
        else:
            logger.info("No recent comparable fixtures displayed")

        return (
            f"{HEADER}\n\n"
            f"{assessment}\n\n"
            f"{distribution}\n\n"
            f"{prediction_text}\n"
            f"{confidence_text}"
            f"{comparable_block}"
        )
