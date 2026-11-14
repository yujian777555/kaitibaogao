"""D-089 public-information budget analytics.

All quantities here are computed from the PUBLIC policy view only:
tool states, compensation contracts, route requires/cost/attempts,
pending flags, learned delays, and the decision budget.  No hidden
outcomes, no true delays, no labels, no min_reachable_harm oracle.
"""
from __future__ import annotations

ACTIVE = ("COMMITTED", "PARTIAL")


def public_min_harm(view) -> int:
    """Lower bound on unavoidable residual using only public info.

    A tool is publicly compensable if it is active, its contract allows
    compensation, and some route's requirements can all reach COMPENSATED
    (fixed point over the requires graph).  Everything else that is active
    is publicly unavoidable.
    """
    compensable = set()
    changed = True
    while changed:
        changed = False
        for tool_id, tool in view["tools"].items():
            if tool_id in compensable:
                continue
            if tool["state"] not in ACTIVE:
                continue
            if not tool["compensation_available"]:
                continue
            for route in tool["routes"]:
                reqs = route["requires"]
                if all(view["tools"].get(r, {}).get("state") == "COMPENSATED"
                       or r in compensable for r in reqs):
                    compensable.add(tool_id)
                    changed = True
                    break
    active = [t for t, tool in view["tools"].items() if tool["state"] in ACTIVE]
    return len([t for t in active if t not in compensable])


def reachable_routes(view, allow_alternate=True, max_attempts=None):
    """Publicly reachable (tool, route) pairs for active tools."""
    out = []
    for tool_id, tool in view["tools"].items():
        if tool["state"] not in ACTIVE or not tool["compensation_available"]:
            continue
        for route in tool["routes"]:
            if route["pending"]:
                continue
            if route["name"] != "primary" and not allow_alternate:
                continue
            if max_attempts is not None and route["attempts"] >= max_attempts:
                continue
            reqs_ok = all(
                view["tools"].get(r, {}).get("state") == "COMPENSATED"
                or (view["tools"].get(r, {}).get("state") in ACTIVE
                    and view["tools"].get(r, {}).get("compensation_available"))
                for r in route["requires"]
            )
            if reqs_ok:
                out.append((tool_id, route))
    return out


def estimate_remaining_decisions(view, learned_delay=None, safety=1.0) -> float:
    """Public anytime estimate: one recovery round per uncompleted tool.

    Per uncompleted compensable tool we estimate the cost of ONE more
    attempt (dispatch + waits + verify).  The estimate is recomputed after
    every observation, so repeated failures naturally inflate the remaining
    cost as attempts and learned delays accumulate.  Assuming all attempts
    would fail up-front (the earlier variant) made the adaptive stop fire
    immediately and is intentionally not used here.
    """
    learned_delay = learned_delay or {}
    total = 0.0
    for tool_id, tool in view["tools"].items():
        if tool["state"] not in ACTIVE:
            continue
        if not tool["compensation_available"]:
            continue
        pending_here = any(r["pending"] for r in tool["routes"])
        if pending_here:
            total += 2  # resolve pending: wait + verify
            continue
        best = None
        for route in tool["routes"]:
            key = (tool_id, route["name"])
            delay = learned_delay.get(key, 1)
            cost = 1 + delay + 1  # one attempt: dispatch + waits + verify
            best = cost if best is None else min(best, cost)
        if best:
            total += best
    total += 1  # terminal action
    return float(total) * safety
