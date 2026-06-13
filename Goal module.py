from dataclasses import dataclass

@dataclass
class GoalNode:
    name: str
    importance: float
    progress: float = 0.0

class GoalEngine:

    def __init__(self):
        self.goals = []

    def add_goal(
        self,
        name,
        importance
    ):
        self.goals.append(
            GoalNode(
                name=name,
                importance=importance
            )
        )

    def update_progress(
        self,
        goal_name,
        delta
    ):

        for goal in self.goals:

            if goal.name == goal_name:

                goal.progress = max(
                    0.0,
                    min(1.0,
                        goal.progress + delta
                    )
                )

    def get_primary_goal(self):

        if not self.goals:
            return None

        return max(
            self.goals,
            key=lambda x:
                x.importance * (1 - x.progress)
        )
