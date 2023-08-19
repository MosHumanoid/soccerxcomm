class TeamScore:
    """The score of a team."""

    def __init__(self, team: str, score: float):
        """Initializes the score of a team.

        Args:
            team: The name of the team.
            score: The score of the team.
        """

        self.team: str = team
        self.score: float = score
