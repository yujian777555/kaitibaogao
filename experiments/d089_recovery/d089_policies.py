"""D-089 budget-cooperative recovery policy (B2 + B3 + B4).

Builds on D088RecoveryPolicy (mechanisms A/B/C + budget-aware dispatch).

B2 Escalation Reserve
  Split the 24-decision budget dynamically:
      B_total = B_recovery + B_verification + B_escalation
  B_escalation is kept at 1 (the terminal action) plus the estimated cost
  of resolving in-flight receipts; recovery dispatch is only allowed while
  the remaining budget covers the worst-case finish (public estimate).

B3 Reachability-Aware Allocation
  Use public_min_harm / reachable_routes to decide when further recovery
  cannot improve the outcome: if the number of active tools equals the
  public unavoidable floor and no reachable route exists, stop.  If
  reachable routes exist but the remaining budget cannot fund them, stop
  early enough to guarantee the terminal action.

B4 Parameterized Strict Stop
  Replace the boolean strict_residual_stop with an evolvable parameter set:
    stop_mode: 0 = legacy (stop_residual), 1 = strict, 2 = adaptive
  In adaptive mode the policy stops when the expected marginal recovery
  (reachable tools x route success evidence) cannot fit in the remaining
  budget after the escalation reserve.
"""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "pilot_a3b"))
sys.path.insert(0, str(_HERE.parent / "d088_recovery"))

from d088_policies import D088RecoveryPolicy  # noqa: E402
from d089_budget import (  # noqa: E402
    public_min_harm, reachable_routes, estimate_remaining_decisions,
)

ACTIVE = ("COMMITTED", "PARTIAL")


class D089BudgetPolicy(D088RecoveryPolicy):
    """Adds B2/B3/B4 budget cooperation on top of the D-088 policy."""

    def __init__(self, genome):
        super().__init__(genome)
        self.stop_mode = getattr(genome, "stop_mode", 2)
        self.escalation_reserve = getattr(genome, "escalation_reserve", 1.0)
        self.cost_safety = getattr(genome, "cost_safety", 1.0)

    # ---- B4: parameterized stop decision ----
    def _should_stop(self, view, available, pending):
        """Return True when stopping now is the budget-cooperative choice."""
        budget = view.get("budget_remaining", 24)
        active = sum(t["state"] in ACTIVE for t in view["tools"].values())
        pmh = public_min_harm(view)

        # B3: nothing publicly reachable -> stop
        if not available and not pending:
            return True

        if self.stop_mode == 0:
            # legacy: stop_residual
            return (active <= self.genome.stop_residual or not available) \
                and budget <= 2 * len(pending) + 1

        if self.stop_mode == 1:
            # strict: only stop when no reachable work remains
            return (not available and not pending)

        # adaptive (default): balance marginal recovery vs escalation safety
        # B2: reserve escalation budget
        resolve_cost = 0.0
        if pending:
            resolve_cost = 2.0 * len(pending)  # worst case wait+verify each
        reserve = self.escalation_reserve + resolve_cost

        # B3: if remaining active equals the public floor and no reachable
        # route exists, stop
        if active <= pmh and not available:
            return True

        if not available:
            return True

        need = estimate_remaining_decisions(
            view, learned_delay=self.learned_delay, safety=self.cost_safety
        )
        # dispatch only if the remaining budget funds recovery AND finish
        if budget <= need + reserve:
            return True
        return False

    def _abort(self, view):
        active = sum(t["state"] in ACTIVE for t in view["tools"].values())
        available = self._available(view)
        budget = view.get("budget_remaining", 24)
        pending = self._pending_tools(view)

        # resolution mode (inherited semantics)
        if pending and not self._can_dispatch_more(view):
            resolved = self._resolve_pending(view)
            if resolved is not None:
                return resolved

        if self._should_stop(view, available, pending):
            if pending:
                resolved = self._resolve_pending(view)
                if resolved is not None:
                    return resolved
            return self._finish((self.genome.stop_action,))

        # B2 gate: never dispatch if the escalation reserve would be spent
        resolve_cost = 2.0 * len(pending)
        if budget <= self.escalation_reserve + resolve_cost + 1:
            if pending:
                resolved = self._resolve_pending(view)
                if resolved is not None:
                    return resolved
            return self._finish((self.genome.stop_action,))

        _score, tool_id, route_name = self._priority(view, available)
        return self._finish_tracked(("COMPENSATE", tool_id, route_name), view)
