class ClientInfo:
    """The information of the client."""

    def __init__(self, team: str, token: str):
        """Initializes the information of the client.

        Args:
            team: The name of the team.
            token: The token of the client.
        """

        self.team: str = team
        self.token: str = token
