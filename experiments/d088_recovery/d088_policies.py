"""D-088 state-conditioned recovery policies with three mechanisms.

A Feedback-Driven Route Switching
  Count FAILED / DEPENDENCY_BLOCKED / CONTRACT_BLOCKED as route failure
  evidence; after ``failure_switch_threshold`` failures on a route, switch to
  its sibling route (even when the genome's ``allow_alternate`` is False —
  the switch is mechanism A's explicit behavior).

B Delay-Aware Adaptive Confirmation
  Fire compensations for all independent tools before waiting (batch
  dispatch); learn each route's receipt delay from the public tick (WAITs
  only); probe VERIFY only after the learned delay elapsed; distinguish
  PENDING from FAILED; never terminate with unresolved receipts.

C Dependency-Aware Path Coordination
  Topologically order tools by public ``requires``; break primary cycles by
  preferring alternate routes for cycle members; boost actions that unlock
  dependent tools; prefer alternates when the primary is permanently
  unreachable (its requires include a contract-blocked tool).

All information is public: tool states, contracts, route metadata
(cost/hint/requires/attempts/last_receipt/pending), decision budget.
"""
from __future__ import annotations

import sys
from pathlib import Path

_D087 = Path(__file__).resolve().parent.parent / "pilot_a3b"
if str(_D087) not in sys.path:
    sys.path.insert(0, str(_D087))

from dependency_policies import BasePolicy  # noqa: E402

BLOCKED_RECEIPTS = ("FAILED", "DEPENDENCY_BLOCKED", "CONTRACT_BLOCKED")


def build_graph(view):
    graph = {}
    for tool_id, tool in view["tools"].items():
        deps = set()
        for route in tool["routes"]:
            for req in route["requires"]:
                deps.add(req)
        graph[tool_id] = sorted(deps)
    return graph


def cycle_tools(graph):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in graph}
    found = set()

    def dfs(node, stack):
        color[node] = GRAY
        for dep in graph.get(node, []):
            if dep not in color:
                continue
            if color[dep] == GRAY:
                cycle = set(stack[stack.index(dep):]) if dep in stack else {dep}
                cycle.add(node)
                found.update(cycle)
            elif color[dep] == WHITE:
                dfs(dep, stack + [dep])
        color[node] = BLACK

    for node in graph:
        if color[node] == WHITE:
            dfs(node, [node])
    return found


def topo_order(graph, done):
    remaining = [n for n in graph if n not in done]
    order = []
    resolved = set(done)
    while remaining:
        ready = [n for n in remaining if all(d in resolved or d not in graph for d in graph[n])]
        if not ready:
            order.extend(sorted(remaining))
            break
        for n in sorted(ready):
            order.append(n)
            resolved.add(n)
        remaining = [n for n in remaining if n not in resolved]
    return order


class D088RecoveryPolicy(BasePolicy):
    def __init__(self, genome):
        super().__init__()
        self.genome = genome
        self.route_failures = {}
        self.route_total_fail = {}
        self.learned_delay = {}
        self.fire_wait_tick = {}
        self.probe_count = {}
        self.wait_ticks = 0

    def _learn_from_probe(self, view):
        """If the previous VERIFY returned PENDING (route still pending), the
        receipt delay is longer than assumed — extend the learned delay."""
        if not self.last_action or self.last_action[0] != "VERIFY":
            return
        tool_id = self.last_action[1]
        for route in view["tools"].get(tool_id, {}).get("routes", []):
            if not route["pending"]:
                continue
            key = (tool_id, route["name"])
            fired = self.fire_wait_tick.get(key, self.wait_ticks)
            elapsed = self.wait_ticks - fired
            self.learned_delay[key] = max(
                self.learned_delay.get(key, 0), elapsed + 1
            )

    # ---- evidence (public feedback) ----
    def _update_evidence(self, view):
        for tool_id, tool in view["tools"].items():
            for route in tool["routes"]:
                key = (tool_id, route["name"])
                attempts = route["attempts"]
                seen = self.seen_attempts.get(key, 0)
                if attempts > seen and route["last_receipt"] in BLOCKED_RECEIPTS:
                    delta = attempts - seen
                    self.failures[key] = self.failures.get(key, 0) + delta
                    self.route_failures[key] = self.route_failures.get(key, 0) + delta
                    self.route_total_fail[key] = self.route_total_fail.get(key, 0) + delta
                elif attempts > seen and route["last_receipt"] == "COMPENSATED":
                    self.route_failures[key] = 0
                # learn receipt delay when a fired route resolves
                if key in self.fire_wait_tick and not route["pending"] and (
                        route["last_receipt"] in ("COMPENSATED", "FAILED")):
                    self.learned_delay[key] = max(
                        0, self.wait_ticks - self.fire_wait_tick[key]
                    )
                    self.fire_wait_tick.pop(key, None)
                    self.probe_count.pop(key, None)
                self.seen_attempts[key] = attempts

    # ---- pending handling ----
    def _pending_tools(self, view):
        out = []
        for tool_id, tool in view["tools"].items():
            for route in tool["routes"]:
                if route["pending"]:
                    out.append((tool_id, route["name"]))
        return out

    def _in_flight(self, view):
        return len(self._pending_tools(view))

    def _can_dispatch_more(self, view):
        """Budget-aware dispatch gate: worst case after one more dispatch we
        need shared waits (<=2 ticks), one VERIFY per in-flight receipt, and
        one terminal action.  Never dispatch if that cannot fit."""
        budget = view.get("budget_remaining", 24)
        in_flight = self._in_flight(view)
        need = in_flight + 5  # 1 dispatch + 2 waits + (in_flight+1) verifies + 1 terminal
        return budget > need

    def _pending_action(self, view):
        pending = self._pending_tools(view)
        if not pending:
            return None
        tool_id, route_name = pending[0]
        key = (tool_id, route_name)
        if not self.genome.allow_verify:
            return ("WAIT",)

        if self.genome.enable_b:
            expected = self.learned_delay.get(key, int(round(self.genome.delay_probe_wait)))
            fired = self.fire_wait_tick.get(key, self.wait_ticks)
            elapsed = self.wait_ticks - fired
            if elapsed < expected:
                # not ready to verify: dispatch other compensations if any
                if self._available(view) and self._can_dispatch_more(view):
                    return None
                return ("WAIT",)
            if self.probe_count.get(key, 0) < self.genome.max_verify_probes:
                self.probe_count[key] = self.probe_count.get(key, 0) + 1
                return ("VERIFY", tool_id)
            # still pending after probes: extend the learned delay and wait
            self.learned_delay[key] = elapsed + 1
            self.probe_count[key] = 0
            return ("WAIT",)

        # legacy fixed cadence (arms L / A / C)
        if self.last_action == ("VERIFY", tool_id):
            return ("WAIT",)
        return ("VERIFY", tool_id)

    # ---- action selection ----
    def _primary_blocked_or_failed(self, tool_id, view):
        tool = view["tools"][tool_id]
        for route in tool["routes"]:
            if route["name"] != "primary":
                continue
            if route["last_receipt"] in BLOCKED_RECEIPTS:
                return True
            if self.route_failures.get((tool_id, "primary"), 0) > 0:
                return True
            # permanently unreachable primary
            for req in route["requires"]:
                req_tool = view["tools"].get(req)
                if req_tool is not None and not req_tool["compensation_available"]:
                    return True
        return False

    def _available(self, view, allow_alternates=True):
        allow = self.genome.allow_alternate
        available = []
        for tool_id, tool in view["tools"].items():
            if tool["state"] not in ("COMMITTED", "PARTIAL"):
                continue
            if not tool["compensation_available"]:
                continue
            for route in tool["routes"]:
                key = (tool_id, route["name"])
                if route["pending"]:
                    continue
                if route["name"] != "primary":
                    if not allow:
                        # mechanism A: failure-driven switch to alternate
                        if not (self.genome.enable_a
                                and self._primary_blocked_or_failed(tool_id, view)):
                            continue
                if route["attempts"] >= self.genome.max_attempts:
                    continue
                if key in self.excluded:
                    continue
                if any(view["tools"].get(r, {}).get("state") != "COMPENSATED"
                       for r in route["requires"]):
                    continue
                available.append((tool_id, route))
        return available

    def _priority(self, view, available):
        tool_ids = list(view["tools"])
        graph = build_graph(view) if self.genome.enable_c else {}
        cycles = cycle_tools(graph) if self.genome.enable_c else set()
        order = topo_order(graph, {
            t for t, tool in view["tools"].items() if tool["state"] == "COMPENSATED"
        }) if self.genome.enable_c else tool_ids
        pos = {tid: i for i, tid in enumerate(order)}
        compensated = {t for t, tool in view["tools"].items() if tool["state"] == "COMPENSATED"}
        pending_now = set(t for t, _ in self._pending_tools(view))
        budget = view.get("budget_remaining", 24)

        scored = []
        for tool_id, route in available:
            key = (tool_id, route["name"])
            score = (
                self.genome.hint_weight * (route["reliability_hint"] == "HIGH")
                + self.genome.cost_weight * route["cost"]
                + self.genome.failure_weight * self.failures.get(key, 0)
                + self.genome.position_weight * tool_ids.index(tool_id)
                + self.genome.dependency_weight * len(route["requires"])
            )
            if self.genome.enable_a:
                score += self.genome.route_failure_penalty * self.route_failures.get(key, 0)
                sibling = (tool_id, "alternate" if route["name"] == "primary" else "primary")
                if self.route_total_fail.get(sibling, 0) >= self.genome.failure_switch_threshold:
                    score += self.genome.alternate_boost
                if route["name"] != "primary" and self._primary_blocked_or_failed(tool_id, view):
                    score += self.genome.alternate_boost
            if self.genome.enable_b:
                if tool_id not in pending_now:
                    score += self.genome.wait_batch_weight
                if budget <= 8:
                    delay = self.learned_delay.get(key, 1)
                    score -= 0.5 * delay * self.genome.wait_batch_weight
            if self.genome.enable_c:
                score += self.genome.topo_order_weight * (
                    len(order) - pos.get(tool_id, len(order))
                ) / max(1, len(order))
                if self.genome.cycle_break_alternate and tool_id in cycles:
                    if route["name"] != "primary":
                        score += self.genome.unlock_priority
                    else:
                        score -= self.genome.topo_order_weight * 0.5
                unlock = sum(
                    1 for dep, reqs in graph.items()
                    if tool_id in reqs and dep not in compensated
                )
                score += self.genome.unlock_priority * 0.2 * unlock
            scored.append((score, tool_id, route["name"]))
        scored.sort(key=lambda item: (-item[0], item[1], item[2]))
        return scored[0]

    def _finish_tracked(self, action, view):
        if action[0] == "COMPENSATE":
            key = (action[1], action[2])
            self.fire_wait_tick[key] = self.wait_ticks
            self.probe_count[key] = 0
        return self._finish(action)

    def _finish(self, action):
        if action == ("WAIT",):
            self.wait_ticks += 1
        self.last_action = action
        return action

    def _resolve_pending(self, view):
        action = self._pending_action(view)
        if action is not None:
            return self._finish(action)
        return None

    def _abort(self, view):
        active = sum(t["state"] in ("COMMITTED", "PARTIAL") for t in view["tools"].values())
        available = self._available(view)
        budget = view.get("budget_remaining", 24)
        pending = self._pending_tools(view)

        # resolution mode: not enough budget to dispatch more and still
        # terminate cleanly -> only resolve receipts
        if pending and not self._can_dispatch_more(view):
            resolved = self._resolve_pending(view)
            if resolved is not None:
                return resolved
        # strict residual stop (R2): never stop while a reachable
        # compensable route remains, unless the budget cannot fit another
        # dispatch cycle.  This prevents early ESCALATE that leaves
        # avoidable residual (R4 failures in R1 round).
        if self.genome.strict_residual_stop and available and self._can_dispatch_more(view):
            _score, tool_id, route_name = self._priority(view, available)
            return self._finish_tracked(("COMPENSATE", tool_id, route_name), view)
        if not available or active <= self.genome.stop_residual or not self._can_dispatch_more(view):
            if pending:
                resolved = self._resolve_pending(view)
                if resolved is not None:
                    return resolved
            return self._finish((self.genome.stop_action,))
        _score, tool_id, route_name = self._priority(view, available)
        return self._finish_tracked(("COMPENSATE", tool_id, route_name), view)

    def act(self, view):
        self._learn_from_probe(view)
        self._update_evidence(view)
        pending = self._pending_tools(view)
        if pending:
            # mechanism B: dispatch independent work while receipts mature
            if (self.genome.enable_b and self._available(view)
                    and self._can_dispatch_more(view)):
                action = self._pending_action(view)
                if action is not None:
                    return self._finish(action)
                # None => dispatch more compensations instead of waiting
            else:
                action = self._pending_action(view)
                if action is not None:
                    return self._finish(action)
        if view["terminal_fault"] == "timeout_before":
            return self._finish(("RETRY_WORKFLOW",))
        if view["terminal_fault"] == "partial_recover":
            return self._recover_current(view)
        return self._abort(view)

    def _recover_current(self, view):
        current = view["current_tool"]
        if view["tools"][current]["state"] == "COMPENSATED":
            return self._finish(("RETRY_WORKFLOW",))
        available = [item for item in self._available(view) if item[0] == current]
        if not available:
            resolved = self._resolve_pending(view)
            if resolved is not None:
                return resolved
            return self._finish((self.genome.stop_action,))
        _score, tool_id, route_name = self._priority(view, available)
        return self._finish_tracked(("COMPENSATE", tool_id, route_name), view)
