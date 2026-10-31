# PUBLIC SKILL: served to anyone through the BotSpot MCP. Never add secrets, customer data or internal details.

"""Price policy for one owned position; order reconciliation is separate.

Call with actual position observations, including confirmed flatness. Keep this
dictionary in self.vars and use separate instances for distinct owned positions.
A missing observation never means flat. Supply only prices known at that time.
"""
import math


class TrailingStopPolicy:
    def __init__(self, state: dict[str, float | None], *, direction: str = "long") -> None:
        if direction not in {"long", "short"}:
            raise ValueError("A trailing policy needs the owned position's direction")
        self.state, self.direction = state, direction
        self.state.setdefault("anchor", None)
        self.state.setdefault("stop", None)

    def observe(self, quantity: float | None, reference_price: float | None = None,
                distance: float | None = None) -> float | None:
        if quantity is None or not math.isfinite(float(quantity)):
            return self.state["stop"]
        if quantity == 0:
            self.state.update(anchor=None, stop=None)
            return None
        if reference_price is not None and math.isfinite(float(reference_price)):
            price = float(reference_price)
            previous = self.state["anchor"]
            self.state["anchor"] = price if previous is None else (
                max(previous, price) if self.direction == "long" else min(previous, price))
        anchor = self.state["anchor"]
        if anchor is None or distance is None or not math.isfinite(float(distance)):
            return self.state["stop"]
        if distance < 0:
            raise ValueError("Trailing distance must be nonnegative")
        candidate = anchor - float(distance) if self.direction == "long" else anchor + float(distance)
        previous_stop = self.state["stop"]
        self.state["stop"] = candidate if previous_stop is None else (
            max(previous_stop, candidate) if self.direction == "long" else min(previous_stop, candidate))
        return self.state["stop"]
