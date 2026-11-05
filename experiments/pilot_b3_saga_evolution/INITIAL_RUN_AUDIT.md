## Pilot B3 initial-run audit — escalation externality found

**Initial run:** GitHub Actions 42025423920  
**Initial code SHA:** 88f478dde6d29de5046701e87b2412360b3f8ebb  
**Status:** SUPERSEDED FOR CLAIMS / PRESERVED AS EXPLORATORY DIAGNOSTIC

The first B3 search run suggested that standard GA and canonical NSGA-II reduced tool actions relative to the manual Saga baseline while retaining task success and zero invariant violations. Inspection of selected genomes revealed a confound: the fitness objective did not constrain escalation rate or account for human handoff cost. Several selected genomes used the partial-response ESCALATE action and/or omitted prefix rollback. Thus a lower tool-action count could be achieved by transferring more unfinished transaction work to a human.

The initial run must not be cited as evidence of evolutionary recovery improvement. Its outputs remain in Git history for auditability.

## Corrective protocol

The corrected B3 run:
1. uses entirely new test seeds 4320–4359 (initial B3 test seeds 4120–4159 are retired and will not be reused);
2. measures escalation rate, rollback completion and unresolved rate;
3. imposes a non-inferiority ceiling on escalation rate: no more than the manual Saga training escalation rate + 0.005;
4. requires zero invariant violations, zero unresolved workflows and task success no lower than manual Saga training success − 0.005;
5. includes an explicit escalation cost of 2.0 action-equivalents in the objective;
6. keeps the same fixed fitness-evaluation budget and validation-only selection.

Only corrected-run results may inform the next research decision. Even if the corrected EC search wins, it remains evidence from a synthetic simulator, not a real LLM/API Agent.
