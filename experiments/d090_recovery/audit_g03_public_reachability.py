import sys, json
sys.path.insert(0, "experiments/d089_recovery"); sys.path.insert(0, "experiments/pilot_a3b"); sys.path.insert(0, "experiments/d088_recovery")
from d089_scenarios import make_scenario
from d089_budget import public_min_harm, reachable_routes
from d088_policies import D088RecoveryPolicy, build_graph, cycle_tools

# verify: g03 view analysis
sc = make_scenario("g03_PAIR_RACE", "D3_DEPENDENT_ABORT", 0)
sys.path.insert(0, "experiments/pilot_a3b")
from dependency_recovery import DependencyRecoveryEnv
env = DependencyRecoveryEnv(sc)
v = env.view()
print("graph:", build_graph(v))
print("cycles:", cycle_tools(build_graph(v)))
print("public_min_harm:", public_min_harm(v))
print("reachable (allow_alt=True):", [(t, r["name"]) for t, r in reachable_routes(v, True, 4)])
print("reachable (allow_alt=False):", [(t, r["name"]) for t, r in reachable_routes(v, False, 4)])
print("g03 requires:", sc["tools"][0]["routes"][0]["requires"], sc["tools"][1]["routes"][0]["requires"])
