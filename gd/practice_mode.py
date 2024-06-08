import time
from copy import deepcopy
from logger import Logger

class PracticeMode:
    """
    A class to manage the practice mode of the game.

    Attributes:
        game (Game): The game instance.
        checkpoints (list[tuple[float, float]]): A list of checkpoint coordinates, each checkpoint is a tuple of (x, y) positions.
        last_checkpoint (tuple[float, float]): The last checkpoint reached by the player.
        last_checkpoint_time (float): The time when the last checkpoint was set.

    """

    def __init__(self, game):
        """
        Constructs all the necessary attributes for the PracticeMode object.

        Args:
            game (Game): The game instance.

        """

        self.game = game
        self.checkpoints = [] # list of checkpoints
        self.last_checkpoint = None # last reached checkpoint
        self.last_checkpoint_time = time.time() # time last checkpoint was set at

    def add_checkpoint(self, checkpoint: tuple[float, float]) -> None:
        """
        Adds a checkpoint to the list and sets it to the most recent checkpoint.

        Args:
            checkpoint (tuple[float, float]): The checkpoint (it's x, y coords) to be added.

        """
        # if player is crashed don't add the checkpoint
        if self.game.is_crashed:
            return

        # deep copy the checkpoint to avoid reference issues
        checkpoint = deepcopy(checkpoint)
        # add the checkpoint to the list of checkpoints
        self.checkpoints.append((checkpoint[0], checkpoint[1]))
        # set the last checkpoint to the most recent checkpoint and reset the last added checkpoint time
        self.last_checkpoint = checkpoint
        self.last_checkpoint_time = time.time()
    
    def remove_checkpoint(self) -> None:
        """
        Removes the most recent checkpoint from the list and updates the last checkpoint reached.

        """
        
        if self.checkpoints:
            self.checkpoints.pop()
            self.last_checkpoint = self.checkpoints[-1] if self.checkpoints else None
            self.last_checkpoint_time = time.time()
        else:
            self.last_checkpoint = None
            self.last_checkpoint_time = time.time()

    def is_checkpoint_time_over(self) -> bool:
        """
        Checks if the time since the last checkpoint was set is greater than 2 seconds.

        """
        return time.time() - self.last_checkpoint_time > 2
    
    def reset_checkpoint_time(self) -> None:
        """
        Resets the time the last checkpoint was added.

        """

        self.last_checkpoint_time = time.time()

    def clear_checkpoints(self) -> None:
        """
        Clears all checkpoint data.

        """

        self.checkpoints = []
        self.last_checkpoint = None
        self.last_checkpoint_time = time.time()

    def is_checkpoint(self) -> bool:
        """
        Checks if there are any checkpoints set.

        """
        return self.last_checkpoint is not None

    def get_last_checkpoint(self) -> tuple[float, float]:
        """
        Returns the last checkpoint reached by the player.

        """
        return self.last_checkpoint[0], self.last_checkpoint[1] if self.last_checkpoint else None