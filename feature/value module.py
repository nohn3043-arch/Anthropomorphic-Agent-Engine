from dataclasses import dataclass

@dataclass
class ValueProfile:
    freedom: float = 0.8
    responsibility: float = 0.7
    dignity: float = 0.9
    intimacy: float = 0.6
    security: float = 0.5

class ValueEngine:

    def __init__(self, profile: ValueProfile):
        self.profile = profile

    def evaluate_event(self, event: str):

        impact = {}

        if event == "force_command":
            impact["freedom"] = -0.4
            impact["dignity"] = -0.2

        elif event == "compliment":
            impact["intimacy"] = 0.2

        elif event == "betrayal":
            impact["security"] = -0.5
            impact["intimacy"] = -0.6

        return impact
