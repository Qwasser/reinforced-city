from enum import Enum
import pygame


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

DIRECTION_VECTORS = [
    (-1, 0),
    (0, -1),
    (+1, 0),
    (0, 1)
]


class StepCycle(Enum):
    FIRST = 0
    SECOND = 1


class PlayerActor(object):
    def __init__(self, y, x, direction=ActorDirections.UP):
        self.direction = direction
        self.step_cycle = StepCycle.FIRST
        self._x = x
        self._y = y
        self._step_counter = 0
        self.size = 16
        self.bullet = None

    def get_action(self, game_state):
        pass

    def _change_step_cycle(self):
        self._step_counter += 1
        self._step_counter %= 3
        if self._step_counter == 0:
            if self.step_cycle == StepCycle.FIRST:
                self.step_cycle = StepCycle.SECOND
            else:
                self.step_cycle = StepCycle.FIRST

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._change_step_cycle()
        self._x = x

    @property
    def y(self):

        return self._y

    @y.setter
    def y(self, y):
        self._change_step_cycle()
        self._y = y


class Bullet(object):
    def __init__(self, y, x, direction=ActorDirections.UP):
        self.x = x
        self.y = y
        self.direction = direction


class DummyPlayer(PlayerActor):
    def get_action(self, game_state):
        return Actions.GO_UP


class PyGameKeyboardPlayer(PlayerActor):
    """
    This player works only if pygame was initialized
    """
    def __init__(self, x, y, direction=ActorDirections.UP):
        super(PyGameKeyboardPlayer, self).__init__(x, y, direction)

    def get_action(self, field):
        pygame.event.get(pygame.KEYDOWN)  # code below does not work without this

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            return Actions.GO_UP

        if keys[pygame.K_a]:
            return Actions.GO_LEFT

        if keys[pygame.K_s]:
            return Actions.GO_DOWN

        if keys[pygame.K_d]:
            return Actions.GO_RIGHT

        if keys[pygame.K_SPACE]:
            return Actions.SHOOT

        return Actions.DO_NOTHING
