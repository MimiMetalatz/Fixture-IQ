def aggregate_outcomes(matches):
    counts = {"H": 0, "D": 0, "A": 0}

    for m in matches:
        outcome = m["metadata"]["outcome"]
        counts[outcome] += 1

    total = sum(counts.values())

    return {
        "rates": {k: v / total for k, v in counts.items()},
        "sample_size": total,
    }
