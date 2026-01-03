class OutcomeDecisionEngine:
    def decide(self, rates: dict, sample_size: int):
        h, d, a = rates["H"], rates["D"], rates["A"]

        best = max(rates, key=rates.get)
        best_rate = rates[best]

        if best_rate < 0.40:
            return {
                "prediction": "no_clear_lean",
                "confidence": "low",
                "rates": rates,
                "sample_size": sample_size,
            }

        if best_rate >= 0.55:
            confidence = "high"
        elif best_rate >= 0.45:
            confidence = "moderate"
        else:
            confidence = "low"

        return {
            "prediction": {"H": "home", "D": "draw", "A": "away"}[best],
            "confidence": confidence,
            "rates": rates,
            "sample_size": sample_size,
        }
