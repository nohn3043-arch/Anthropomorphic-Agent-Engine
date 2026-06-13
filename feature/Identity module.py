from dataclasses import dataclass

@dataclass
class IdentityNode:
    name: str
    strength: float
    priority: float

class IdentityEngine:

    def __init__(self):
        self.identities = []

    def add_identity(
        self,
        name,
        strength,
        priority
    ):
        self.identities.append(
            IdentityNode(
                name,
                strength,
                priority
            )
        )

    def compute_conflict(self):

        if len(self.identities) < 2:
            return 0.0

        total = 0.0

        for i in range(len(self.identities)):
            for j in range(i+1, len(self.identities)):

                a = self.identities[i]
                b = self.identities[j]

                total += abs(
                    a.priority - b.priority
                )

        return min(1.0, total)
