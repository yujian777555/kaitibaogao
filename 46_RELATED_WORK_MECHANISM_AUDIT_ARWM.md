# Related-work mechanism audit — Agent training, world models and evolutionary control

Date: 2026-11-05
Status: first-pass mechanism audit; full paper/code replication not completed.

## Mechanism matrix

| Work | Learned/evolved object | Feedback/data | Optimization mechanism | Overlap with this thesis | Remaining distinction to test |
|---|---|---|---|---|---|
| TRACE (2026) | LoRA adapters for missing agent capabilities | Contrasts successful/failed trajectories; synthesizes capability-targeted environments | RL per capability; adapter routing | Failure-driven agent training and online self-improvement are already established | Our candidate keeps API LLM frozen and trains action-conditional tool-state/risk predictor; EC searches an external recovery controller. Must prove this is more than an auxiliary predictor |
| SENTINEL (2026) | Solver policy | Controller diagnoses failures; proposer synthesizes targeted tasks | RL on failure-targeted tasks | Failure-driven curriculum and controller-proposer-solver loop are not novel | Our candidate uses simulator-verified paired interventions to train action-outcome/risk model, then uses it to screen EC candidates under fixed real rollout budget |
| HarnessMDP (2026) | Structural execution controller around frozen LLM | Offline rollouts, terminal task-rubric rewards | Advantage-weighted regression | A frozen LLM with learned external controller is directly established | Our candidate optimizes finite-state recovery policies with EC and a calibrated action-conditional risk model; must compare against offline controller and ensure no advantage from more data |
| CoMAP (EMNLP 2026) | Textual world model and agent policy | On-policy trajectories; predicted next textual state; self-distillation | Closed-loop co-evolution and future-aware reflection | Closest world-model/agent co-evolution work; rules out generic “train world model and improve agent” claim | CoMAP predicts textual next-state feedback and co-evolves policy/world model. Candidate difference is structured side-effect/effect-state transition, paired counterfactual action interventions, explicit invariant-risk calibration, and world-model-assisted evolutionary controller search. This difference must be checked against full paper and code |
| EvoTool (ACL 2026) | Modular tool-use prompts: Planner, Selector, Caller, Synthesizer | Diagnostic trajectories and LLM critique | Blame-aware targeted mutation + diversity-aware selection | Tool-policy evolutionary self-improvement is already established | Our search object is executable recovery state machine with effect-state contracts, not four natural-language tool-use prompts. Must benchmark against EvoTool or a faithful adaptation |
| Generic surrogate-assisted EA | Candidate solution and surrogate predictor | Evaluated candidate/fitness pairs | Surrogate ranking, infill, uncertainty sampling | Model-assisted evolutionary search itself is mature | Need a domain-specific algorithmic contribution and demonstrate gain beyond standard surrogate EA |
| Model-based RL / offline RL | Policy/value/world model | Logged transitions and rewards | Model-based planning or offline policy learning | Learned transition models and controller optimization are established | Need explain why EC is preferable/beneficial versus offline RL or model-predictive control under discrete contract-constrained policies |

## Primary-source evidence

### CoMAP
ACL Anthology page: https://aclanthology.org/2026.emnlp-main.1200/
arXiv: https://arxiv.org/abs/2606.02372
Official code: https://github.com/loyiv/CoMAP

The paper describes a textual world model that predicts future environment feedback for candidate actions. The agent assesses prediction reliability and revises actions; resulting on-policy trajectories update the world model through self-distillation. The released repository's world-model dataset prompt asks for one-step next textual state given current textual state, task goal, interaction history and action. The world-model loss combines next-state token CE with teacher-logit distillation. The round manager orchestrates rollout, buffer export, world-model training and policy update. Thus CoMAP already covers closed-loop world-model/policy co-evolution. It does not, from the inspected README and code files, establish our specific structured effect-state risk-head + paired counterfactual intervention + EC policy-search combination; the full paper must still be audited before claiming distinction.

### HarnessMDP
Paper: https://arxiv.org/abs/2607.05458

The paper models harness operation as finite-horizon MDP with structural actions (observe, retrieve, call-tool, draft, check, revise, submit), freezes LLM executor parameters/prompts, and trains controller from offline rollouts using advantage-weighted regression. It emphasizes that outcome improvement is limited by high-return support in the offline buffer. This is a direct baseline for any learned external recovery controller.

### TRACE
Paper: https://arxiv.org/abs/2604.05336

TRACE contrasts successful and failed trajectories to identify missing capabilities, synthesizes capability-targeted environments, trains LoRA adapters by RL, and routes adapters at inference. Therefore “train on Agent failures using A800” is not novel by itself.

### SENTINEL
Paper: https://arxiv.org/abs/2606.12908

SENTINEL uses Controller–Proposer–Solver: analyze failures, generate targeted executable tasks, train Solver via RL. Failure-targeted data generation and iterative solver training are already covered.

### EvoTool
ACL Anthology: https://aclanthology.org/2026.acl-long.2016/
Official code: https://github.com/SYang2000/ACL_2026_EvoTool

EvoTool evolves Planner, Selector, Caller and Synthesizer prompt modules through trajectory-grounded blame attribution, feedback-guided targeted mutation and diversity-aware population selection. A new paper cannot claim these generic mechanisms as novel.

## Preliminary novelty boundary

Do NOT claim as novel:
- training an LLM/LoRA from failure trajectories;
- generic textual world models for tool agents;
- closed-loop world-model/policy co-evolution;
- learning an external controller around a frozen LLM;
- evolutionary prompt/tool-use policy optimization;
- generic surrogate-assisted EA or uncertainty sampling.

Potential research hypothesis only:
A simulator-grounded, action-conditional counterfactual model jointly predicts structured effect-state transitions, postcondition satisfaction and side-effect/invariant risk; a contract-constrained EA uses calibrated risk upper bounds and OOD abstention to select recovery-controller candidates under a fixed real-rollout budget. Its value must be established against CoMAP-style world-model loop, HarnessMDP-style learned controller, standard surrogate EA and no-surrogate GA/GP/NSGA.

## What remains unverified

1. Full CoMAP paper ablations and exact training/evaluation budgets.
2. TRACE/SENTINEL training recipe, dataset split and model sizes.
3. HarnessMDP complete action space, reward and released implementation.
4. Fair, executable reproductions/adaptations of CoMAP and HarnessMDP.
5. Prior work on uncertainty-aware surrogate-assisted EA and safety-constrained model-based search in discrete program/controller spaces.
6. Whether a structured predictor beats LightGBM/MLP on the small state/action schema.
7. Whether any model-assisted method improves the best real policy under identical true rollout budget.

## Current decision

The A800/ARWM candidate remains HOLD. No GPU training is authorized by this audit. Pilot A initial slice shows a competent hand-coded state-aware policy matches oracle task success/safety; a richer bounded Pilot A-2 is required before implementing EA or training ARWM.
