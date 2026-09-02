"""
SPL Agent Engine — Composable feature modules.

Each module is self-contained and can be mixed into a persona:
    - identity:  multi-identity system with identity conflict
    - goal:      goal hierarchy and goal-engine dynamics
    - bias:      cognitive bias profiles (optimistic / paranoid / depressive)
    - value:     value system and dissonance
    - world:     world-model priors (optimistic / pessimistic / traumatized)
    - language_style: internal-state → spoken-line style renderer (persona-level)
"""

from .identity import IdentityNode, IdentityEngine
from .goal import GoalNode, GoalEngine
from .bias import BiasProfile, BiasEngine
from .value import ValueProfile, ValueEngine
from .world import WorldModel
from .language_style import LanguagePersona, StyleProfile, LanguageStyleEngine

__all__ = [
    "IdentityNode", "IdentityEngine",
    "GoalNode", "GoalEngine",
    "BiasProfile", "BiasEngine",
    "ValueProfile", "ValueEngine",
    "WorldModel",
    "LanguagePersona", "StyleProfile", "LanguageStyleEngine",
]
