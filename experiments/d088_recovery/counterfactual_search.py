"""D-088 counterfactual reachability search over D-087 failure scenarios.

Beam-search over legal public actions to find short successful sequences for
the six repeat-4 failure scenarios (rv02/rv03/rv04 x R3/R4).  The search uses
only the environment transition function; sequences are evidence that better
policies exist within the 24-decision budget.  No hidden outcome information
is used for action legality: actions are chosen from the public view, and the
search oracle only ranks complete episodes by their public report.
"""
from __future__ import annotations

import heapq
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "pilot_a3b"))

from d087_challenge import make_scenario  # noqa: E402
from dependency_recovery import DependencyRecoveryEnv  # noqa: E402

MAX_ACTIONS = 24


def legal_actions(view):
    actions = []
    pending_any = False
    for tool_id, tool in view["tools"].items():
        if tool["state"] in ("COMMITTED", "PARTIAL"):
            for route in tool["routes"]:
                if not route["pending"]:
                    actions.append(("COMPENSATE", tool_id, route["name"]))
        for route in tool["routes"]:
            if route["pending"]:
                actions.append(("VERIFY", tool_id))
                pending_any = True
    # de-duplicate VERIFY
    seen = set()
    uniq = []
    for a in actions:
        if a not in seen:
            seen.add(a)
            uniq.append(a)
    if not pending_any:
        uniq.append(("ESCALATE",))
        uniq.append(("WAIT",))
    else:
        uniq.append(("WAIT",))
    return uniq


def score_report(rep):
    """Lower is better. Feasible-first, then class success, then harm/cost."""
    constraint = rep["constraint_violation"]
    return (
        constraint,
        0 if rep["class_success"] else 1,
        rep["avoidable_harm"],
        rep["decision_count"],
    )


def env_clone(env):
    import copy
    return copy.deepcopy(env)


def beam_search(scenario, beam=400, max_actions=MAX_ACTIONS):
    """Beam search: state = (env, history). Expand legal actions."""
    start = DependencyRecoveryEnv(scenario)
    beam_states = [(score_report(start.report()) + (0,), start, [])]
    best = None
    for depth in range(max_actions):
        candidates = []
        for _s, env, hist in beam_states:
            if env.terminal_action is not None:
                rep = env.report()
                sc = score_report(rep)
                if best is None or sc < best[0]:
                    best = (sc, hist, rep)
                continue
            if env.task_success():
                rep = env.report()
                sc = score_report(rep)
                if best is None or sc < best[0]:
                    best = (sc, hist, rep)
                continue
            for action in legal_actions(env.view()):
                if action == ("ESCALATE",) and depth < 2:
                    continue
                nenv = env_clone(env)
                nenv.step(action)
                nhist = hist + [action]
                rep = nenv.report()
                sc = score_report(rep)
                if nenv.terminal_action is not None:
                    if best is None or sc < best[0]:
                        best = (sc, nhist, rep)
                    continue
                # rank partial states: prefer fewer active tools, zero pending
                active = sum(
                    1 for st in nenv.tools.values() if st in ("COMMITTED", "PARTIAL")
                )
                pend = nenv.pending_count()
                rank = (rep["constraint_violation"], active + pend, nenv.decision_count)
                candidates.append((rank, nenv, nhist))
        if not candidates:
            break
        candidates.sort(key=lambda x: x[0])
        beam_states = candidates[:beam]
        # early stop if best is a clean class success at depth <= 12
        if best is not None and best[0][1] == 0 and best[0][0] == 0 and len(best[1]) <= 12:
            break
    return best


def main():
    out = {}
    for family in ("rv02_CROSS_DELAY", "rv03_MULTI_ROUTE", "rv04_REVERSE_RECOVERY"):
        for stratum, label in (("D3_DEPENDENT_ABORT", "R3"), ("D4_BLOCKED_COMPENSATION", "R4")):
            key = f"{family}|{stratum}|r4"
            sc = make_scenario(family, stratum, 4)
            best = beam_search(sc, beam=300)
            if best is None:
                out[key] = {"found": False}
                continue
            score, hist, rep = best
            out[key] = {
                "found": True,
                "class_success": rep["class_success"],
                "label": rep["label"],
                "decision_count": rep["decision_count"],
                "avoidable_harm": rep["avoidable_harm"],
                "residual_side_effects": rep["residual_side_effects"],
                "constraint_violation": rep["constraint_violation"],
                "sequence": [list(a) for a in hist],
            }
            print(key, "->", out[key]["class_success"], "dec=", out[key]["decision_count"])
    Path(HERE / "counterfactual_results.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
