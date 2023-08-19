import datetime
from typing import Dict, List

from .game_stage_kind import GameStageKind
from .team_score import TeamScore


class GameInfo:
    """The information of the game."""

    def __init__(self, stage: GameStageKind, start_time: datetime.datetime,
                 end_time: datetime.datetime, score_list: List[TeamScore], simulation_rate: float):
        """Initializes the information of the game.

        Args:
            stage: The stage of the game.
            start_time: The start time of the game.
            end_time: The end time of the game.
            score_list: The score of the teams.
            simulation_rate: The simulation rate of the game.
        """

        self.stage: GameStageKind = stage
        self.start_time: datetime.datetime = start_time
        self.end_time: datetime.datetime = end_time
        self.score: Dict[str, TeamScore] = {
            score.team: score for score in score_list
        }
        self.simulation_rate: float = simulation_rate
