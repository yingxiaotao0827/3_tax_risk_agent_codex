from enum import Enum


class AgentState(str, Enum):
    THINK = "think"
    EVALUATE_EVIDENCE = "evaluate_evidence"
    ACT = "act"
    OBSERVE = "observe"
    CHECK_BUDGET = "check_budget"
    RESOLVE_CONFLICT = "resolve_conflict"
    CONCLUDE = "conclude"
    HUMAN_REVIEW = "human_review"

