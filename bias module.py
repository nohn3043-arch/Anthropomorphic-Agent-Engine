from dataclasses import dataclass

@dataclass
class BiasProfile:

    negativity_bias: float = 0.7
    confirmation_bias: float = 0.6
    projection_bias: float = 0.4

class BiasEngine:

    def __init__(self, profile):

        self.profile = profile

    def amplify_memory(
        self,
        event_type,
        strength
    ):

        if event_type in [
            "insult",
            "betrayal"
        ]:

            strength *= (
                1 +
                self.profile.negativity_bias
            )

        return strength
