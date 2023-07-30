from enum import Enum


class GameStageKind(Enum):
    """Game stage kind.
    
    Attributes:
        READY: The game is ready to start.
        IN_PROGRESS: The game is in progress.
        PAUSED: The game is paused.
        FINISHED: The game is finished.
        ABORTED: The game is aborted.
    """

    READY = "ready"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    FINISHED = "finished"
    ABORTED = "aborted"
