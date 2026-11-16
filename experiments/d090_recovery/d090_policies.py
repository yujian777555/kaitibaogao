"""D-090 policy fixes: pair-race, exhaustive fallback, completion gate.

Inherits D089BudgetPolicy (B2/B3/B4).  Adds three togglable structural
mechanisms (all public information only):

P1 pair_race_alternate
  Detect dependency cycles among active tools.  A cycle member's primary
  route that requires another active cycle member is deadlock-blocked;
  treat that primary as failed evidence and allow its alternate.

P2 exhaustive_fallback
  When the normal available set is empty but active > public_min_harm,
  re-search ALL routes (including alternates regardless of allow_alternate,
  and routes beyond exclusions) whose requires are strictly COMPENSATED.
  This fixes the local-vs-global reachability misjudgement found in g03.

P3 completion_gate
  Never stop while active > public_min_harm and the budget can fund one
  more dispatch cycle.  This generalises strict stop to "stop only when
  the publicly unavoidable floor is reached".

P4 harm_first_ordering
  When the budget is tight (below a threshold), prefer routes that clear
  residual with fewest decisions (immediate / low-cost), so more tools get
  cleared before the budget runs out — reducing avoidable harm.
"""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "pilot_a3b"))
sys.path.insert(0, str(_HERE.parent / "d088_recovery"))
sys.path.insert(0, str(_HERE.parent / "d089_recovery"))

from d088_policies import BLOCKED_RECEIPTS, build_graph, cycle_tools  # noqa: E402
from d089_policies import D089BudgetPolicy, ACTIVE  # noqa: E402
from d089_budget import public_min_harm  # noqa: E402


class D090Policy(D089BudgetPolicy):
    def __init__(self, genome):
        super().__init__(genome)
        self.pair_race_alternate = getattr(genome, "pair_race_alternate", True)
        self.exhaustive_fallback = getattr(genome, "exhaustive_fallback", True)
        self.completion_gate = getattr(genome, "completion_gate", True)
        self.harm_first_ordering = getattr(genome, "harm_first_ordering", True)
        self.harm_order_mode = getattr(genome, "harm_order_mode", 1)
        self.pair_rule = getattr(genome, "pair_rule", 0)
        self.fallback_mode = getattr(genome, "fallback_mode", 2)
        self.completion_mode = getattr(genome, "completion_mode", 1)
        self.harm_budget_threshold = getattr(genome, "harm_budget_threshold", 8)

    # ---- P1: deadlock-aware blocked-primary detection ----
    def _primary_deadlocked(self, tool_id, view):
        """Primary requires another active cycle member -> circular deadlock."""
        tool = view["tools"][tool_id]
        graph = build_graph(view)
        cycles = cycle_tools(graph)
        if tool_id not in cycles or self.pair_rule == 1:
            return False
        for route in tool["routes"]:
            if route["name"] != "primary":
                continue
            for req in route["requires"]:
                req_tool = view["tools"].get(req)
                if (req_tool is not None and req in cycles
                        and req_tool["state"] in ACTIVE
                        and req_tool["state"] != "COMPENSATED"):
                    return True
        return False

    def _primary_blocked_or_failed(self, tool_id, view):
        if super()._primary_blocked_or_failed(tool_id, view):
            return True
        return self.pair_race_alternate and self._primary_deadlocked(tool_id, view)

    def _pair_filtered_available(self, view, available):
        """互依环存在未完成工具时，先清空该子图再派发其他工具。"""
        if self.pair_rule == 1:
            return available
        cycles = cycle_tools(build_graph(view))
        active_cycle = {
            tool_id for tool_id in cycles
            if view["tools"].get(tool_id, {}).get("state") in ACTIVE
        }
        if not active_cycle:
            return available
        if any(route["pending"]
               for tool_id in active_cycle
               for route in view["tools"][tool_id]["routes"]):
            return []
        pair_routes = [item for item in available if item[0] in active_cycle]
        return pair_routes or available

    def _available(self, view, allow_alternates=True):
        available = super()._available(view, allow_alternates=allow_alternates)
        return self._pair_filtered_available(view, available)

    # ---- P2: exhaustive fallback when locally empty but globally reachable ----
    def _fallback_available(self, view):
        """All routes whose requires are STRICTLY COMPENSATED, ignoring
        allow_alternate / exclusions / max_attempts caps (last resort)."""
        out = []
        for tool_id, tool in view["tools"].items():
            if tool["state"] not in ACTIVE or not tool["compensation_available"]:
                continue
            for route in tool["routes"]:
                if route["pending"]:
                    continue
                if all(view["tools"].get(r, {}).get("state") == "COMPENSATED"
                       for r in route["requires"]):
                    out.append((tool_id, route))
        return out

    def _available_or_fallback(self, view):
        available = self._available(view)
        if available:
            return available
        if self.exhaustive_fallback or self.fallback_mode == 2:
            pmh = public_min_harm(view)
            active = sum(t["state"] in ACTIVE for t in view["tools"].values())
            if active > pmh:
                return self._fallback_available(view)
        return []

    # ---- P4: residual-minimizing ordering under tight budget ----
    def _priority(self, view, available):
        score = super()._priority(view, available)
        if not self.harm_first_ordering:
            return score
        budget = view.get("budget_remaining", 24)
        if budget > self.harm_budget_threshold or self.harm_order_mode == 0:
            return score
        # tight budget: re-rank so cheap/immediate routes come first
        def tight_key(item):
            _s, tool_id, route_name = item
            route = next(r for r in view["tools"][tool_id]["routes"]
                         if r["name"] == route_name)
            # prefer: fewer requires (more likely to fire), lower cost,
            # immediate receipts (idempotent flag correlates with delay=0)
            return (len(route["requires"]), route["cost"],
                    0 if route["idempotent"] else 1, tool_id, route_name)
        candidates = []
        for tool_id, route in available:
            candidates.append((0.0, tool_id, route["name"]))
        return min(candidates, key=tight_key)

    # ---- P3: completion gate ----
    def _should_stop(self, view, available, pending):
        if self.completion_gate or self.completion_mode >= 1:
            pmh = public_min_harm(view)
            active = sum(t["state"] in ACTIVE for t in view["tools"].values())
            if active > pmh and (available or self._fallback_available(view)) \
                    and self._can_dispatch_more(view):
                return False
        if self.completion_mode == 2 and active > pmh and self._can_dispatch_more(view):
            return False
        return super()._should_stop(view, available, pending)

    def _abort(self, view):
        active = sum(t["state"] in ACTIVE for t in view["tools"].values())
        available = self._available_or_fallback(view)
        budget = view.get("budget_remaining", 24)
        pending = self._pending_tools(view)

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

        if not self._can_dispatch_more(view):
            if pending:
                resolved = self._resolve_pending(view)
                if resolved is not None:
                    return resolved
            return self._finish((self.genome.stop_action,))

        if not available:
            if pending:
                resolved = self._resolve_pending(view)
                if resolved is not None:
                    return resolved
            return self._finish((self.genome.stop_action,))

        _score, tool_id, route_name = self._priority(view, available)
        return self._finish_tracked(("COMPENSATE", tool_id, route_name), view)
