import numpy as np
from sprites import SpriteStorage
from actors import PyGameKeyboardPlayer, Bullet
import pygame

import enums

BLOCK_COUNT = 13

STATIC_OBJ_PER_BLOCK = 2
SPRITES_PER_OBJ = 2

PIXELS_PER_BLOCK = 16

STATIC_SPRITE_TYPE_COUNT = 4


class MapBuilder(object):
    MAP_SIZE = BLOCK_COUNT * STATIC_OBJ_PER_BLOCK * SPRITES_PER_OBJ

    def __init__(self):
        self._map = np.zeros((self.MAP_SIZE, self.MAP_SIZE), dtype=np.uint8)

    def add_bricks(self, x, y):
        base = enums.StaticObjectTypes.BRICK.value * STATIC_SPRITE_TYPE_COUNT

        x *= SPRITES_PER_OBJ
        y *= SPRITES_PER_OBJ

        self._map[y, x] = base + 1
        self._map[y, x + 1] = base + 2
        self._map[y + 1, x] = base + 3
        self._map[y + 1, x + 1] = base + 4

        return self

    def get_map(self):
        return self._map.copy()


class GameState(object):
    BOARD_SIZE = BLOCK_COUNT * PIXELS_PER_BLOCK

    def __init__(self, map):
        self.map = map
        self.actors = []

    def add_actor(self, actor):
        self.actors.append(actor)
        return self


class GameEngine(object):
    def __init__(self, game_state):
        self._state = game_state

    def _apply_action(self, actor):
        action = actor.get_action(self._state)
        if action == enums.Actions.GO_UP:
            actor.direction = enums.ActorDirections.UP
            if self._check_can_move(actor, actor.x, actor.y - 1):
                actor.y -= 1
            else:
                actor.y = actor.y

        if action == enums.Actions.GO_DOWN:
            actor.direction = enums.ActorDirections.DOWN
            if self._check_can_move(actor, actor.x, actor.y + 1):
                actor.y += 1
            else:
                actor.y = actor.y

        if action == enums.Actions.GO_LEFT:
            actor.direction = enums.ActorDirections.LEFT
            if self._check_can_move(actor, actor.x - 1, actor.y):
                actor.x -= 1
            else:
                actor.x = actor.x

        if action == enums.Actions.GO_RIGHT:
            actor.direction = enums.ActorDirections.RIGHT
            if self._check_can_move(actor, actor.x + 1, actor.y):
                actor.x += 1
            else:
                actor.x = actor.x

        if actor.bullet is not None:
            delta_y, delta_x = enums.DIRECTION_VECTORS[actor.bullet.direction.value]
            delta_y, delta_x = delta_y * 2, delta_x * 2
            actor.bullet.x += delta_x
            actor.bullet.y += delta_y

            max_cor = self._state.BOARD_SIZE - actor.size
            if not(0 <= actor.bullet.x <= max_cor and 0 <= actor.bullet.y <= max_cor):
                actor.bullet = None

        if action == enums.Actions.SHOOT:
            if actor.bullet is None:
                if actor.direction == enums.ActorDirections.UP:
                    actor.bullet = Bullet(actor.y - 3, actor.x + 6, actor.direction)

                if actor.direction == enums.ActorDirections.DOWN:
                    actor.bullet = Bullet(actor.y + 16, actor.x + 6, actor.direction)

                if actor.direction == enums.ActorDirections.LEFT:
                    actor.bullet = Bullet(actor.y + 6, actor.x - 3, actor.direction)

                if actor.direction == enums.ActorDirections.RIGHT:
                    actor.bullet = Bullet(actor.y + 6, actor.x + 16, actor.direction)

    def _check_can_move(self, actor, new_x, new_y):
        max_cor = self._state.BOARD_SIZE - actor.size
        if 0 <= new_x <= max_cor and 0 <= new_y <= max_cor:
            if np.sum(self._state.map[new_y / 4: (new_y + actor.size + 3) / 4,
                                      new_x / 4: (new_x + actor.size + 3) / 4]) == 0:
                return True
        return False

    def tick(self):
        for actor in game_state.actors:
            self._apply_action(actor)


class Renderer(object):
    OFF_BOARD_SPACE = 8

    def __init__(self, game_state, screen, scale=4):
        self.size = (game_state.BOARD_SIZE + self.OFF_BOARD_SPACE * 2) * scale
        self._scale = scale
        self._game_state = game_state
        self._sprite_storage = SpriteStorage('../data/tank_sprite.png', self._scale)

        self._screen = screen
        self._screen.init_screen(self.size, self._sprite_storage.palette)

        self._render_env()

    def render(self):
        for actor in self._game_state.actors:
            sprite = self._sprite_storage.get_tank_actor_sprite(actor)
            self._lay_sprite(sprite, actor.x, actor.y)

            bullet = actor.bullet
            if bullet is not None:
                sprite = self._sprite_storage.get_bullet_actor_sprite(bullet)
                self._lay_sprite(sprite, bullet.x, bullet.y)

        return self._screen

    def _render_env(self):
        for x in xrange(self._game_state.map.shape[0]):
            for y in xrange(self._game_state.map.shape[1]):
                obj_index = self._game_state.map[y, x]
                if obj_index != 0:
                    sprite = self._sprite_storage.get_static_object_sprite(obj_index - 1)
                    self._lay_sprite(sprite, x * 4, y * 4)

    def _lay_sprite(self, sprite, x, y):
        x += self.OFF_BOARD_SPACE
        y += self.OFF_BOARD_SPACE

        self._screen.put_sprite(sprite, (x * self._scale, y * self._scale, sprite.shape[1], sprite.shape[0]))


class PyGameScreen(object):
    def __init__(self):
        self._screen = None
        self._palette = None

    def init_screen(self, size, palette=None):
        self._screen = pygame.display.set_mode((size, size))
        self._palette = palette

    def _make_surface(self, sprite):
        sprite_sf = pygame.surfarray.make_surface(sprite)
        i_p = iter(self._palette)
        sprite_sf.set_palette(list(zip(i_p, i_p, i_p)))
        return sprite_sf

    def put_sprite(self, sprite, rect):
        self._screen.blit(self._make_surface(sprite), rect)


if __name__ == "__main__":
    map_builder = MapBuilder()

    for i in range(5, 10):
        for j in range(5, 10):
            map_builder.add_bricks(i, j)

    map = map_builder.get_map()
    game_state = GameState(map).add_actor(PyGameKeyboardPlayer(192, 0, enums.ActorSpriteEnum.QUICK_TANK))

    pygame.init()

    engine = GameEngine(game_state)
    renderer = Renderer(game_state, PyGameScreen())

    clock = pygame.time.Clock()
    while True:
        engine.tick()
        image = renderer.render()
        pygame.display.flip()
        # pygame.time.delay(5)
