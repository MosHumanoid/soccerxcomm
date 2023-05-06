from enum import Enum

class GameStageKind(Enum):
    """Game stage kind."""
    
    READY = "ready"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    FINISHED = "finished"
    ABORTED = "aborted"
