from enum import Enum


class Actions(Enum):
    DO_NOTHING = 0
    SHOOT = 1
    GO_UP = 2
    GO_LEFT = 3
    GO_DOWN = 4
    GO_RIGHT = 5


class ActorDirections(Enum):
    """
    This corresponds to sprite sheet
    """
    UP = 0
    LEFT = 1
    DOWN = 2
    RIGHT = 3


class StepCycle(Enum):
    FIRST = 0
    SECOND = 1


class PlayerActor(object):
    def __init__(self, y, x, direction=ActorDirections.UP):
        self.direction = direction
        self.step_cycle = StepCycle.FIRST
        self.x = x
        self.y = y

    def get_action(self, game_state):
        pass


class DummyPlayer(PlayerActor):
    def get_action(self, game_state):
        return Actions.GO_UP


class KeyBoardPlayer(PlayerActor):
    def __init__(self, keyboard, direction):
        super(KeyBoardPlayer, self).__init__(direction)

    def get_action(self, field):
        pass
