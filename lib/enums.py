from enum import Enum


class ActorSpriteEnum(Enum):
    PLAYER_1_TANK = 0
    BULLET = 1
    QUICK_TANK = 2


TANK_SPRITES = {
    ActorSpriteEnum.PLAYER_1_TANK,
    ActorSpriteEnum.QUICK_TANK
}


class StaticObjectTypes(Enum):
    BRICK = 0
    CONCRETE = 1


class Actions(Enum):
    GO_UP = 0
    GO_LEFT = 1
    GO_DOWN = 2
    GO_RIGHT = 3
    DO_NOTHING = 4
    SHOOT = 5


class ActorDirections(Enum):
    """
    This corresponds to sprite sheet
    """
    UP = 0
    LEFT = 1
    DOWN = 2
    RIGHT = 3

DIRECTION_VECTORS = [
    (-1, 0),    # UP
    (0, -1),    # LEFT
    (+1, 0),    # DOWN
    (0, 1)      # RIGHT
]


BULLET_COLLISION_RECTANGLES = [
    (0, 0, 3, 4),
    (0, 0, 4, 3),
    (0, 0, 3, 4),
    (0, 0, 4, 3),
]

BULLET_SPRITE_RECTS = [
    (3, 6, 3, 4),
    (2, 6, 4, 3),
    (3, 6, 3, 4),
    (2, 6, 4, 3),
]

BULLET_TANK_SHIFTS = [
    (6, -4),
    (-4, 6),
    (6, 16),
    (16, 6),
]

TANK_COLLISION_RECTANGLE = (0, 0, 16, 16)


class TankAnimationCycle(Enum):
    FIRST = 0
    SECOND = 1


def get_collision_rect(actor_sprite_type, direction):
    if actor_sprite_type == ActorSpriteEnum.BULLET:
        return BULLET_COLLISION_RECTANGLES[direction.value]
    else:
        return TANK_COLLISION_RECTANGLE
