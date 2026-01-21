import math
from typing import List


class VectorValidationError(Exception):
    """Raised when a vector fails validation."""
    pass


def validate_vector(
    values: List[float],
    expected_dim: int,
    record_id: str | None = None,
):
    """
    Validate a single vector before upsert.

    Checks:
    - correct dimensionality
    - numeric values only
    - no NaN / inf
    """

    if len(values) != expected_dim:
        raise VectorValidationError(
            f"Vector dimension mismatch"
            f"{f' (id={record_id})' if record_id else ''}: "
            f"expected {expected_dim}, got {len(values)}"
        )

    for i, v in enumerate(values):
        if not isinstance(v, (int, float)):
            raise VectorValidationError(
                f"Non-numeric value in vector"
                f"{f' (id={record_id})' if record_id else ''} "
                f"at dim {i}: {v}"
            )

        if math.isnan(v) or math.isinf(v):
            raise VectorValidationError(
                f"Invalid numeric value in vector"
                f"{f' (id={record_id})' if record_id else ''} "
                f"at dim {i}: {v}"
            )
